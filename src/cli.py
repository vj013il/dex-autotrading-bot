import argparse
from validator.core import CryptoValidator

def main():
    parser = argparse.ArgumentParser(description='Validate crypto addresses')
    parser.add_argument('--currency', '-c', required=True, help='Cryptocurrency ticker')
    parser.add_argument('--address', '-a', required=True, help='Wallet address')
    
    args = parser.parse_args()
    
    try:
        is_valid = CryptoValidator.validate(args.currency, args.address)
        print(f"Address {args.address} is {'VALID' if is_valid else 'INVALID'}")
        exit(0 if is_valid else 1)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(2)

if __name__ == "__main__":
    main()
