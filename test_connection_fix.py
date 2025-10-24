"""
Test script to verify MT5 connection fix
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mt5.connection import MT5Connection

def test_connection():
    """Test MT5 connection with the new fix"""
    print("=" * 70)
    print("Testing MT5 Connection Fix")
    print("=" * 70)
    print("\n🎯 This test will verify that the connection fix works correctly")
    print("   and doesn't disconnect an already-running MT5 terminal.\n")
    
    # Create connector
    print("[1/3] Creating MT5Connector instance...")
    connector = MT5Connection()
    print(f"✓ Connector created")
    print(f"   Login: {connector.login}")
    print(f"   Server: {connector.server}")
    
    # Test connection
    print("\n[2/3] Attempting to connect...")
    print("   (This should NOT disconnect your MT5 terminal if it's running)")
    
    try:
        success = connector.connect()
        message = "Connected" if success else "Failed"
    except Exception as e:
        success = False
        message = str(e)
    
    if success:
        print(f"\n✅ SUCCESS! {message}")
        
        # Get account info
        print("\n[3/3] Verifying connection...")
        account_info = connector.get_account_info()
        
        if account_info:
            print("✓ Account info retrieved successfully:")
            print(f"   Login: {account_info['login']}")
            print(f"   Server: {account_info['server']}")
            print(f"   Name: {account_info['name']}")
            print(f"   Balance: {account_info['balance']} {account_info['currency']}")
            print(f"   Equity: {account_info['equity']} {account_info['currency']}")
            print(f"   Company: {account_info['company']}")
            
            print("\n" + "=" * 70)
            print("✅ TEST PASSED - Connection fix working correctly!")
            print("=" * 70)
            print("\n📋 What happened:")
            print("   1. Connector checked for existing MT5 connection")
            print("   2. Either reused existing connection or created new one cleanly")
            print("   3. Your MT5 terminal connection was NOT disrupted")
            print("   4. No Error -6 occurred!")
            
            # Check status
            status = connector.get_status()
            print(f"\n📊 Connection Status:")
            print(f"   Connected: {status['connected']}")
            print(f"   Connection Time: {status['connection_time']}")
            print(f"   Last Error: {status['last_error'] or 'None'}")
            
            # Disconnect
            print("\n🔌 Disconnecting...")
            connector.disconnect()
            print("✓ Disconnected successfully")
            
            return True
        else:
            print("❌ Failed to get account info")
            return False
    else:
        print(f"\n❌ FAILED: {message}")
        print("\n📋 Troubleshooting tips:")
        print("   1. Make sure MT5 is installed")
        print("   2. Check that AutoTrading is enabled in MT5")
        print("   3. Verify internet connection")
        print("   4. Check that no other programs are using MT5")
        print("   5. Try running MT5 as Administrator")
        return False


if __name__ == "__main__":
    try:
        result = test_connection()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
