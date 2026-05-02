import json
import demo_core_engine as e

print("=== RESET ===")
state = e.reset_demo(100.0)
print(json.dumps(state, ensure_ascii=False, indent=2))

print("\n=== TICK 1 ===")
print(json.dumps(e.tick(), ensure_ascii=False, indent=2))

print("\n=== TICK 2 ===")
print(json.dumps(e.tick(), ensure_ascii=False, indent=2))

print("\n=== EQUITY ===")
print(e.equity())
