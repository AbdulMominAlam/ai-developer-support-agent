from tools import lookup_account, create_ticket

#import secrets
#for my API token
#print(secrets.token_hex(32))

print("\n--- Test 1: Valid Account Lookup ---")
result = lookup_account("ACC-1001")
print(result)


print("\n--- Test 2: Another Valid Account Lookup ---")
result = lookup_account("ACC-1002")
print(result)


print("\n--- Test 3: Suspended Account Lookup ---")
result = lookup_account("ACC-1003")
print(result)


print("\n--- Test 4: Invalid Account Lookup ---")
result = lookup_account("ACC-9999")
print(result)


print("\n--- Test 5: Create Database Support Ticket ---")
result = create_ticket(
    account_id="ACC-1001",
    category="Database issue",
    description="The database connection keeps failing."
)
print(result)


print("\n--- Test 6: Create API Usage Ticket ---")
result = create_ticket(
    account_id="ACC-1002",
    category="API usage",
    description="The account has reached its monthly API call limit."
)
print(result)


print("\n--- Test 7: Create Authentication Ticket ---")
result = create_ticket(
    account_id="ACC-1003",
    category="Authentication issue",
    description="Users are unable to sign in with email and password."
)
print(result)


print("\n--- Test 8: Create Ticket for Invalid Account ---")
result = create_ticket(
    account_id="ACC-9999",
    category="General issue",
    description="This ticket should not be created."
)
print(result)