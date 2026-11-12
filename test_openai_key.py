import os
import sys
import getpass

try:
    from openai import OpenAI, AuthenticationError, RateLimitError, APIError
except ImportError:
    print("[ERROR] The 'openai' library is not installed.")
    print("Please install it using: pip install openai")
    sys.exit(1)


def check_openai_key(api_key: str):
    print("\n" + "=" * 50)
    print("           OPENAI API KEY CREDIT TEST")
    print("=" * 50)
    masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"Testing key: {masked_key}\n")

    client = OpenAI(api_key=api_key)

    # Step 1: Check basic authentication
    print("[1/2] Verifying API key validity...")
    try:
        # Listing models verifies if the key is structurally and cryptographically valid
        client.models.list()
        print("  -> Authentication successful! API key is valid.")
    except AuthenticationError as e:
        print(f"  [FAILED] Authentication failed: {e.message}")
        print("\nResult: The API key is INVALID or has been revoked.")
        return False
    except APIError as e:
        print(f"  [ERROR] An unexpected API error occurred: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Connection error: {e}")
        return False

    # Step 2: Make a minimal generation request to test available credit/quota
    # Note: listing models succeeds even if balance is $0.
    # Only an actual generation request checks if the account has active quota/credit.
    print("\n[2/2] Testing available credit/quota (sending 1-token test prompt)...")
    
    test_models = ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o"]
    
    for model_name in test_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            print(f"  -> Test completion successful using model: {response.model}")
            print("\n" + "=" * 50)
            print("RESULT: KEY HAS ACTIVE CREDIT!")
            print("Your OpenAI API key is active and has available quota.")
            print("=" * 50 + "\n")
            return True

        except RateLimitError as e:
            print(f"  -> RateLimitError on '{model_name}': {e.message}")
            err_body = getattr(e, "body", {}) or {}
            err_code = err_body.get("code") if isinstance(err_body, dict) else None

            print("\n" + "=" * 50)
            if err_code == "insufficient_quota" or "quota" in str(e).lower():
                print("RESULT: NO CREDIT / QUOTA EXCEEDED (429)")
                print("The API key is valid, but the account has $0 balance or has exhausted its credits.")
                print("To fix this, add payment credits at: https://platform.openai.com/settings/organization/billing")
            else:
                print("RESULT: RATE LIMITED (429)")
                print("The request hit a rate limit, but the key may still have active credit.")
            print("=" * 50 + "\n")
            return False

        except APIError as e:
            # If the specific model is not found / not permitted, try the next fallback model
            if "model" in str(e).lower() and ("not found" in str(e).lower() or "does not exist" in str(e).lower()):
                continue
            print(f"  [FAILED] API request failed: {e}")
            print("\n" + "=" * 50)
            print("RESULT: UNABLE TO USE KEY")
            print(f"Details: {e.message if hasattr(e, 'message') else e}")
            print("=" * 50 + "\n")
            return False

        except Exception as e:
            print(f"  [ERROR] Unexpected error: {e}")
            return False


def main():
    api_key = None

    # 1. Check command line arguments
    if len(sys.argv) > 1:
        api_key = sys.argv[1].strip()

    # 2. Check environment variable
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("Found API key in environment variable OPENAI_API_KEY.")

    # 3. Prompt user if not found
    if not api_key:
        try:
            api_key = input("Enter your OpenAI API key (or press Enter to exit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(0)

    check_openai_key(api_key)


if __name__ == "__main__":
    main()
