from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum

from .models import Customer, Loan
from .serializers import (
    CustomerSerializer, CustomerRegistrationSerializer,
    LoanEligibilitySerializer, LoanEligibilityResponseSerializer,
    LoanCreateSerializer, LoanResponseSerializer,
    LoanDetailSerializer, CustomerLoanSerializer
)

class CustomerRegistrationView(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_serializer = CustomerSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoanEligibilityView(APIView):
    def post(self, request):
        serializer = LoanEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate credit score
        credit_score = self._calculate_credit_score(customer, loan_amount)
        
        # Check if sum of current EMIs > 50% of monthly salary
        current_loans = Loan.objects.filter(customer=customer, status='APPROVED')
        total_monthly_emi = current_loans.aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0
        
        # Calculate monthly installment for the new loan
        monthly_installment = Loan.calculate_monthly_installment(loan_amount, interest_rate, tenure)
        
        # Check if total EMIs (including new loan) would exceed 50% of salary
        if (total_monthly_emi + monthly_installment) > (0.5 * customer.monthly_salary):
            approval = False
            corrected_interest_rate = interest_rate
        else:
            # Determine approval and corrected interest rate based on credit score
            approval, corrected_interest_rate = self._determine_approval_and_rate(credit_score, interest_rate)
        
        response_data = {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': monthly_installment
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _calculate_credit_score(self, customer, loan_amount):
        # Initialize credit score
        credit_score = 100
        
        # Get all loans for this customer
        loans = Loan.objects.filter(customer=customer)
        
        # If sum of current loans > approved limit, credit score = 0
        current_debt = loans.filter(status='APPROVED').aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
        if current_debt + loan_amount > customer.approved_limit:
            return 0
        
        # Calculate components for credit score
        if loans.exists():
            # Past loans paid on time
            total_emis = loans.aggregate(Sum('tenure'))['tenure__sum'] or 0
            on_time_emis = loans.aggregate(Sum('emis_paid_on_time'))['emis_paid_on_time__sum'] or 0
            if total_emis > 0:
                on_time_ratio = on_time_emis / total_emis
                # Adjust score based on payment history (max impact: 40 points)
                credit_score -= 40 * (1 - on_time_ratio)
            
            # Number of loans taken in past (max impact: 20 points)
            num_loans = loans.count()
            if num_loans > 5:
                credit_score -= 20
            elif num_loans > 3:
                credit_score -= 10
            
            # Loan activity in current year (max impact: 20 points)
            from django.utils import timezone
            current_year = timezone.now().year
            loans_this_year = loans.filter(start_date__year=current_year).count()
            if loans_this_year > 3:
                credit_score -= 20
            elif loans_this_year > 1:
                credit_score -= 10
            
            # Loan approved volume relative to salary (max impact: 20 points)
            loan_volume_ratio = current_debt / customer.monthly_salary
            if loan_volume_ratio > 24:  # More than 2 years of salary
                credit_score -= 20
            elif loan_volume_ratio > 12:  # More than 1 year of salary
                credit_score -= 10
        
        return max(0, credit_score)  # Ensure score is not negative
    
    def _determine_approval_and_rate(self, credit_score, interest_rate):
        if credit_score > 50:
            # Approve loan with given interest rate
            return True, interest_rate
        elif credit_score > 30:
            # Approve loans with interest rate > 12%
            if interest_rate > 12:
                return True, interest_rate
            else:
                return True, 12.0
        elif credit_score > 10:
            # Approve loans with interest rate > 16%
            if interest_rate > 16:
                return True, interest_rate
            else:
                return True, 16.0
        else:
            # Don't approve any loans
            return False, interest_rate

class LoanCreateView(APIView):
    def post(self, request):
        serializer = LoanCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check eligibility
        eligibility_view = LoanEligibilityView()
        credit_score = eligibility_view._calculate_credit_score(customer, loan_amount)
        
        # Calculate monthly installment
        monthly_installment = Loan.calculate_monthly_installment(loan_amount, interest_rate, tenure)
        
        # Check if total EMIs would exceed 50% of salary
        current_loans = Loan.objects.filter(customer=customer, status='APPROVED')
        total_monthly_emi = current_loans.aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0
        
        if (total_monthly_emi + monthly_installment) > (0.5 * customer.monthly_salary):
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "EMIs would exceed 50% of monthly salary",
                "monthly_installment": monthly_installment
            }, status=status.HTTP_200_OK)
        
        # Determine approval based on credit score
        approval, corrected_interest_rate = eligibility_view._determine_approval_and_rate(credit_score, interest_rate)
        
        if not approval:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": "Low credit score",
                "monthly_installment": monthly_installment
            }, status=status.HTTP_200_OK)
        
        # If interest rate needs correction and is different from requested
        if corrected_interest_rate != interest_rate:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": f"Interest rate should be at least {corrected_interest_rate}%",
                "monthly_installment": monthly_installment
            }, status=status.HTTP_200_OK)
        
        # Create the loan
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure,
            monthly_repayment=monthly_installment,
            status='APPROVED',
            start_date=None,  # Will be set when loan is disbursed
            end_date=None     # Will be calculated when loan is disbursed
        )
        
        # Update customer's current debt
        customer.current_debt += loan_amount
        customer.save()
        
        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": "Loan approved",
            "monthly_installment": monthly_installment
        }, status=status.HTTP_201_CREATED)

class LoanDetailView(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomerLoansView(APIView):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer, status='APPROVED')
        serializer = CustomerLoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
