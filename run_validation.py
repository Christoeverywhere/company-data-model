from models import CompanyMetadata
from sample_data_final import SAMPLE_COMPANIES
from pydantic import ValidationError

def validate_all():
    passed = 0
    failed = 0
    errors = []
    
    for idx, comp in enumerate(SAMPLE_COMPANIES):
        try:
            CompanyMetadata(**comp)
            passed += 1
        except ValidationError as e:
            failed += 1
            name = comp.get("Company Name", f"Unknown (index {idx})")
            errors.append((name, str(e)))
            
    print(f"Validation complete. Passed: {passed}, Failed: {failed}")
    for name, err in errors:
        print(f"\\n--- Failed Validation for: {name} ---")
        print(err)

if __name__ == "__main__":
    validate_all()
