from django.db import models
from django.utils import timezone
import math

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def calculate_approved_limit(cls, monthly_salary):
        # Approved limit = 36 * monthly_salary (rounded to nearest lakh)
        limit = 36 * monthly_salary
        # Round to nearest lakh (100,000)
        return round(limit / 100000) * 100000

class Loan(models.Model):
    LOAN_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
    ]
    
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.FloatField()
    tenure = models.IntegerField()  # in months
    interest_rate = models.FloatField()  # in percentage
    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.name}"
    
    @property
    def repayments_left(self):
        if self.status == 'PAID':
            return 0
        
        months_passed = 0
        if self.start_date:
            today = timezone.now().date()
            months_passed = (today.year - self.start_date.year) * 12 + today.month - self.start_date.month
        
        return max(0, self.tenure - months_passed)
    
    @classmethod
    def calculate_monthly_installment(cls, loan_amount, interest_rate, tenure):
        # Convert annual interest rate to monthly and decimal form
        monthly_interest_rate = interest_rate / (12 * 100)
        
        # Compound interest formula for EMI calculation
        emi = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** tenure) / (((1 + monthly_interest_rate) ** tenure) - 1)
        
        return round(emi, 2)
