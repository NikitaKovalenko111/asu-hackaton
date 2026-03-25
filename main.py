import asyncio
import random

from classes.pump import Pump


def generate_sensor_values(pump: Pump) -> dict:
    """Generate normal or anomalous sensor values based on pump anomaly_active flag."""
    if pump.anomaly_active:
        # Anomaly: values outside normal range
        return {
            "petrol_pressure_input": random.uniform(0.8, 1.2),
            "petrol_pressure_output": random.uniform(1.5, 2.0),
            "front_bearing_pump_temperature": random.uniform(70.0, 95.0),
            "rear_bearing_pump_temperature": random.uniform(70.0, 95.0),
        }
    else:
        # Normal range
        return {
            "petrol_pressure_input": random.uniform(0.264, 0.410),
            "petrol_pressure_output": random.uniform(0.423, 0.694),
            "front_bearing_pump_temperature": random.uniform(49.0, 50.0),
            "rear_bearing_pump_temperature": random.uniform(49.0, 50.0),
        }


async def run_pump(pump_name: str, pump: Pump, period_seconds: float) -> None:
    pump.start_pump()

    while True:
        # Generate sensor values (normal or anomalous)
        values = generate_sensor_values(pump)
        pump.iteration(
            petrol_pressure_input=values["petrol_pressure_input"],
            petrol_pressure_output=values["petrol_pressure_output"],
            front_bearing_pump_temperature=values["front_bearing_pump_temperature"],
            rear_bearing_pump_temperature=values["rear_bearing_pump_temperature"],
            #vertical_front_bearing_pump_vibration=0.99,
            #horizontal_front_bearing_pump_vibration=0.49,
            #vertical_rear_bearing_pump_vibration=0.47,
            #horizontal_rear_bearing_pump_vibration=1.07,
            #axial_rear_bearing_pump_vibration=0.49,
        )

        print(
            f"{pump_name}: state={pump.state}, "
            f"p_in={pump.petrol_pressure_input:.3f}, p_out={pump.petrol_pressure_output:.3f}, "
            f"t_front={pump.front_bearing_pump_temperature:.2f}, t_rear={pump.rear_bearing_pump_temperature:.2f}",
            f"{'[ANOMALY]' if pump.anomaly_active else ''}"
        )
        await asyncio.sleep(period_seconds)


async def button_handler(pumps: dict) -> None:
    """Listen for user input to trigger anomalies on pumps."""
    print("\n--- Anomaly Controller ---")
    print("Press: 1 = anomaly pump-1, 2 = anomaly pump-2, 3 = anomaly pump-3")
    print("       a = clear all anomalies")
    print("       q = quit\n")

    loop = asyncio.get_event_loop()
    
    while True:
        try:
            # Run input in thread pool to avoid blocking
            user_input = await loop.run_in_executor(None, input, "> ")
            user_input = user_input.strip().lower()

            if user_input == "1" and "pump-1" in pumps:
                pumps["pump-1"].trigger_anomaly()
                print("⚠️  Anomaly triggered on pump-1")
            elif user_input == "2" and "pump-2" in pumps:
                pumps["pump-2"].trigger_anomaly()
                print("⚠️  Anomaly triggered on pump-2")
            elif user_input == "3" and "pump-3" in pumps:
                pumps["pump-3"].trigger_anomaly()
                print("⚠️  Anomaly triggered on pump-3")
            elif user_input == "a":
                for pump in pumps.values():
                    pump.clear_anomaly()
                print("✓ All anomalies cleared")
            elif user_input == "q":
                print("Exiting...")
                break
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")


async def main() -> None:
    pumps = {
        "pump-1": Pump(
            petrol_pressure_input=random.uniform(0.264, 0.410),
            petrol_pressure_output=random.uniform(0.423, 0.694),
            front_bearing_pump_temperature=random.uniform(49.0, 50.0),
            rear_bearing_pump_temperature=random.uniform(49.0, 50.0),
        ),
        "pump-2": Pump(
            petrol_pressure_input=random.uniform(0.264, 0.410),
            petrol_pressure_output=random.uniform(0.423, 0.694),
            front_bearing_pump_temperature=random.uniform(49.0, 50.0),
            rear_bearing_pump_temperature=random.uniform(49.0, 50.0),
        ),
        "pump-3": Pump(
            petrol_pressure_input=random.uniform(0.264, 0.410),
            petrol_pressure_output=random.uniform(0.423, 0.694),
            front_bearing_pump_temperature=random.uniform(49.0, 50.0),
            rear_bearing_pump_temperature=random.uniform(49.0, 50.0),
        )
    }
    periods = {
        "pump-1": 1.0,
        "pump-2": 1.2,
        "pump-3": 1.5,
    }

    pump_tasks = [
        asyncio.create_task(run_pump(name, pump, periods[name]))
        for name, pump in pumps.items()
    ]
    
    button_task = asyncio.create_task(button_handler(pumps))
    
    all_tasks = pump_tasks + [button_task]
    
    try:
        await asyncio.gather(*all_tasks)
    except asyncio.CancelledError:
        pass
    finally:
        # Stop all tasks
        for task in all_tasks:
            task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user")