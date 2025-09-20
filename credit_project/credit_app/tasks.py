import os
import pandas as pd
from celery import shared_task
from django.utils import timezone
from datetime import datetime
from .models import Customer, Loan

@shared_task
def ingest_customer_data(file_path):
    """
    Ingest customer data from Excel file into the database
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Process each row
        for _, row in df.iterrows():
            # Check if customer already exists
            customer_id = row.get('customer_id')
            if customer_id and Customer.objects.filter(customer_id=customer_id).exists():
                continue
            
            # Create new customer
            Customer.objects.create(
                customer_id=customer_id if customer_id else None,  # Allow auto-increment if not provided
                first_name=row.get('first_name', ''),
                last_name=row.get('last_name', ''),
                age=row.get('age', 0),  # Default age to 0 if missing
                phone_number=str(row.get('phone_number', '')),
                monthly_salary=row.get('monthly_salary', 0),
                approved_limit=row.get('approved_limit', 0),
                current_debt=row.get('current_debt', 0.0)
            )
        
        return f"Successfully ingested {len(df)} customer records"
    except Exception as e:
        return f"Error ingesting customer data: {str(e)}"

@shared_task
def ingest_loan_data(file_path):
    """
    Ingest loan data from Excel file into the database
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Process each row
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                # Get customer
                customer_id = row.get('customer_id')
                try:
                    customer = Customer.objects.get(customer_id=customer_id)
                except Customer.DoesNotExist:
                    error_count += 1
                    continue
                
                # Check if loan already exists
                loan_id = row.get('loan_id')
                if loan_id and Loan.objects.filter(loan_id=loan_id).exists():
                    continue
                
                # Parse dates
                start_date = None
                if 'start_date' in row and pd.notna(row['start_date']):
                    if isinstance(row['start_date'], str):
                        start_date = datetime.strptime(row['start_date'], '%Y-%m-%d').date()
                    else:
                        start_date = row['start_date'].date() if hasattr(row['start_date'], 'date') else None
                
                end_date = None
                if 'end_date' in row and pd.notna(row['end_date']):
                    if isinstance(row['end_date'], str):
                        end_date = datetime.strptime(row['end_date'], '%Y-%m-%d').date()
                    else:
                        end_date = row['end_date'].date() if hasattr(row['end_date'], 'date') else None
                
                # Create new loan
                Loan.objects.create(
                    loan_id=loan_id if loan_id else None,  # Allow auto-increment if not provided
                    customer=customer,
                    loan_amount=row.get('loan_amount', 0.0),
                    tenure=row.get('tenure', 0),
                    interest_rate=row.get('interest_rate', 0.0),
                    monthly_repayment=row.get('monthly_repayment', 0.0),
                    emis_paid_on_time=row.get('EMIs_paid_on_time', 0),
                    start_date=start_date,
                    end_date=end_date,
                    status='APPROVED'  # Assuming all imported loans are approved
                )
                
                success_count += 1
            except Exception as e:
                error_count += 1
                continue
        
        return f"Successfully ingested {success_count} loan records. Errors: {error_count}"
    except Exception as e:
        return f"Error ingesting loan data: {str(e)}"

@shared_task
def process_data_files():
    """
    Process both customer and loan data files
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Define file paths
    customer_file = os.path.join(base_dir, 'data', 'customer_data.xlsx')
    loan_file = os.path.join(base_dir, 'data', 'loan_data.xlsx')
    
    # Process files if they exist
    results = []
    
    if os.path.exists(customer_file):
        result = ingest_customer_data(customer_file)
        results.append(result)
    else:
        results.append(f"Customer data file not found at {customer_file}")
    
    if os.path.exists(loan_file):
        result = ingest_loan_data(loan_file)
        results.append(result)
    else:
        results.append(f"Loan data file not found at {loan_file}")
    
    return results