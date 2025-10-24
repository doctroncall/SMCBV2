"""
MT5 Symbol Checker
This script helps diagnose available symbols in your MT5 terminal
"""
import MetaTrader5 as mt5
import sys

def check_symbols():
    """Check and display available symbols in MT5"""
    
    print("=" * 60)
    print("MT5 Symbol Checker")
    print("=" * 60)
    
    # Initialize MT5
    print("\n[1] Initializing MT5...")
    if not mt5.initialize():
        print(f"✗ Failed to initialize MT5: {mt5.last_error()}")
        return False
    
    print("✓ MT5 initialized successfully")
    
    # Get terminal info
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"\nTerminal: {terminal_info.name}")
        print(f"Company: {terminal_info.company}")
        print(f"Connected: {terminal_info.connected}")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        print(f"Account: {account_info.login}")
        print(f"Server: {account_info.server}")
        print(f"Broker: {account_info.company}")
    
    print("\n" + "=" * 60)
    print("[2] Checking for GBPUSD symbol...")
    print("=" * 60)
    
    # Check for GBPUSD specifically
    search_terms = ["GBPUSD", "GBP", "POUND", "CABLE"]
    
    all_symbols = mt5.symbols_get()
    if all_symbols is None or len(all_symbols) == 0:
        print("✗ No symbols available!")
        return False
    
    print(f"\n✓ Total symbols available: {len(all_symbols)}")
    
    # Search for GBPUSD-related symbols
    print(f"\nSearching for GBPUSD-related symbols...")
    gbp_symbols = []
    
    for symbol in all_symbols:
        symbol_upper = symbol.name.upper()
        for term in search_terms:
            if term in symbol_upper:
                gbp_symbols.append(symbol)
                break
    
    if gbp_symbols:
        print(f"\n✓ Found {len(gbp_symbols)} GBP-related symbols:")
        print("-" * 60)
        for symbol in gbp_symbols[:20]:  # Show first 20
            visible = "✓" if symbol.visible else "✗"
            print(f"  {visible} {symbol.name:20s} - {symbol.description}")
        
        if len(gbp_symbols) > 20:
            print(f"  ... and {len(gbp_symbols) - 20} more")
    else:
        print("\n✗ No GBP-related symbols found!")
    
    # Show common forex symbols
    print("\n" + "=" * 60)
    print("[3] Common Forex Symbols Available:")
    print("=" * 60)
    
    common_pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF"]
    
    for pair in common_pairs:
        # Try exact match
        info = mt5.symbol_info(pair)
        if info:
            visible = "✓" if info.visible else "✗"
            print(f"  {visible} {pair}")
        else:
            # Try to find similar
            found = []
            for symbol in all_symbols:
                if pair.upper() in symbol.name.upper():
                    found.append(symbol.name)
            
            if found:
                print(f"  ✗ {pair} not found, but similar: {', '.join(found[:3])}")
            else:
                print(f"  ✗ {pair} not available")
    
    # Show all visible forex symbols
    print("\n" + "=" * 60)
    print("[4] All Visible Forex Symbols:")
    print("=" * 60)
    
    forex_symbols = []
    for symbol in all_symbols:
        if symbol.visible and any(cur in symbol.name.upper() for cur in ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]):
            forex_symbols.append(symbol)
    
    if forex_symbols:
        print(f"\n✓ Found {len(forex_symbols)} visible forex symbols:")
        for symbol in forex_symbols[:30]:  # Show first 30
            print(f"  - {symbol.name:20s} - {symbol.description}")
        
        if len(forex_symbols) > 30:
            print(f"  ... and {len(forex_symbols) - 30} more")
    else:
        print("\n✗ No visible forex symbols found!")
    
    print("\n" + "=" * 60)
    print("[5] Recommendation:")
    print("=" * 60)
    
    # Find the best GBPUSD match
    best_match = None
    for symbol in gbp_symbols:
        if "USD" in symbol.name.upper() and "GBP" in symbol.name.upper():
            best_match = symbol
            break
    
    if best_match:
        print(f"\n✓ Recommended symbol to use: {best_match.name}")
        print(f"  Description: {best_match.description}")
        print(f"  Visible: {best_match.visible}")
        
        # Try to select it
        if not best_match.visible:
            print(f"\n  Attempting to make symbol visible...")
            if mt5.symbol_select(best_match.name, True):
                print(f"  ✓ Successfully selected {best_match.name}")
            else:
                error = mt5.last_error()
                print(f"  ✗ Failed to select: {error}")
        
        print(f"\n  To use this symbol in your code, use: '{best_match.name}'")
    else:
        print("\n✗ No suitable GBPUSD symbol found!")
        print("  Please check your broker's symbol list in MT5 terminal")
        print("  Or contact your broker for the correct symbol name")
    
    # Cleanup
    mt5.shutdown()
    print("\n" + "=" * 60)
    print("✓ Check complete!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = check_symbols()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
