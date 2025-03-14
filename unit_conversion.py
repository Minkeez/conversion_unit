from typing import Union, Callable, Dict, Tuple
import re
import argparse
from fastapi import FastAPI

__version__ = "1.0.2"
__author__ = "Phumin 'HourCode' Udomdach"

# Conversion factors for simple multiplications
CONVERSION_FACTORS: Dict[Tuple[str, str], float] = {
    # Length
    ("m", "cm"): 100.0, ("cm", "m"): 0.01,
    ("m", "km"): 0.001, ("km", "m"): 1000.0,
    ("m", "in"): 39.3701, ("in", "m"): 1 / 39.3701,
    ("m", "ft"): 3.28084, ("ft", "m"): 0.3048,
    ("km", "mi"): 0.621371, ("mi", "km"): 1.60934,
    ("yd", "ft"): 3.0, ("ft", "yd"): 1 / 3.0,
    ("in", "ft"): 1 / 12.0, ("ft", "in"): 12.0,
    ("mi", "yd"): 1760.0, ("yd", "mi"): 1 / 1760.0,
    ("nm", "m"): 1e-9, ("m", "nm"): 1e9,  # Nanometers
    ("au", "km"): 149597870.7, ("km", "au"): 1 / 149597870.7,  # Astronomical Units
    ("ly", "km"): 9.461e12, ("km", "ly"): 1 / 9.461e12,  # Lightyears
    
    # Mass
    ("kg", "g"): 1000.0, ("g", "kg"): 0.001,
    ("kg", "lb"): 2.20462, ("lb", "kg"): 0.453592,
    ("g", "mg"): 1000.0, ("mg", "g"): 0.001,
    ("oz", "g"): 28.3495, ("g", "oz"): 1 / 28.3495,
    ("lb", "oz"): 16.0, ("oz", "lb"): 1 / 16.0,
    ("ton", "kg"): 1000.0, ("kg", "ton"): 1 / 1000.0,
    
    # Derived Units
    ("n", "lbf"): 0.224809, ("lbf", "n"): 4.44822,  # Force
    ("nm", "lb-ft"): 0.737562, ("lb-ft", "nm"): 1.35582,  # Torque
    ("kg/m3", "lb/ft3"): 0.062428, ("lb/ft3", "kg/m3"): 16.0185,  # Density
}

# Temperature conversions using functions
TEMPERATURE_CONVERSIONS: Dict[Tuple[str, str], Callable[[float], float]] = {
    ("c", "f"): lambda v: (v * 9/5) + 32,
    ("f", "c"): lambda v: (v - 32) * 5/9,
    ("c", "k"): lambda v: v + 273.15,
    ("k", "c"): lambda v: v - 273.15,
    ("f", "k"): lambda v: (v - 32) * 5/9 + 273.15,
    ("k", "f"): lambda v: (v - 273.15) * 9/5 + 32
}

def convert(value: Union[int, float], from_unit: str, to_unit: str) -> float:
    """Convert a value from one unit to another."""
    from_unit, to_unit = from_unit.lower(), to_unit.lower()
    
    if (from_unit, to_unit) in CONVERSION_FACTORS:
        return value * CONVERSION_FACTORS[(from_unit, to_unit)]
    
    elif (from_unit, to_unit) in TEMPERATURE_CONVERSIONS:
        return TEMPERATURE_CONVERSIONS[(from_unit, to_unit)](value)
    
    else:
        raise ValueError(f"Conversion from '{from_unit}' to '{to_unit}' is not supported.")

# CLI Support
def cli():
    parser = argparse.ArgumentParser(description="Unit Conversion CLI Tool")
    parser.add_argument("value", type=float, help="Value to convert")
    parser.add_argument("from_unit", type=str, help="Unit to convert from")
    parser.add_argument("to_unit", type=str, help="Unit to convert to")
    args = parser.parse_args()
    
    try:
        result = convert(args.value, args.from_unit, args.to_unit)
        print(f"{args.value} {args.from_unit} = {result} {args.to_unit}")
    except ValueError as e:
        print(e)

# REST API (FastAPI)
app = FastAPI()

@app.get("/convert")
def api_convert(value: float, from_unit: str, to_unit: str):
    try:
        result = convert(value, from_unit, to_unit)
        return {"result": result}
    except ValueError as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cli()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
