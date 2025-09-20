from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'name', 'age', 'monthly_salary', 'approved_limit', 'phone_number']
        read_only_fields = ['customer_id', 'approved_limit']

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']
    
    monthly_income = serializers.IntegerField(write_only=True)
    
    def create(self, validated_data):
        monthly_income = validated_data.pop('monthly_income')
        approved_limit = Customer.calculate_approved_limit(monthly_income)
        
        customer = Customer.objects.create(
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            **validated_data
        )
        return customer

class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class LoanEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()

class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['customer_id', 'loan_amount', 'interest_rate', 'tenure']
    
    customer_id = serializers.IntegerField(write_only=True)
    
    def create(self, validated_data):
        customer_id = validated_data.pop('customer_id')
        customer = Customer.objects.get(customer_id=customer_id)
        
        loan_amount = validated_data['loan_amount']
        interest_rate = validated_data['interest_rate']
        tenure = validated_data['tenure']
        
        monthly_repayment = Loan.calculate_monthly_installment(loan_amount, interest_rate, tenure)
        
        loan = Loan.objects.create(
            customer=customer,
            monthly_repayment=monthly_repayment,
            status='APPROVED',
            **validated_data
        )
        return loan

class LoanResponseSerializer(serializers.ModelSerializer):
    loan_id = serializers.IntegerField(read_only=True)
    customer_id = serializers.IntegerField(source='customer.customer_id', read_only=True)
    loan_approved = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)
    monthly_installment = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer_id', 'loan_approved', 'message', 'monthly_installment']

class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_repayment', 'tenure']

class CustomerLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_repayment', 'repayments_left']