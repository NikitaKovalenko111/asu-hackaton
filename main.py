import asyncio
import random

from classes.pump import Pump


def generate_sensor_values(pump: Pump) -> dict:
    petrol_pressure_input = random.uniform(0.264, 0.410)
    petrol_pressure_output = random.uniform(0.423, 0.694)
    front_bearing_pump_temperature = random.uniform(49.0, 50.0+(50*pump.work_coef))
    rear_bearing_pump_temperature = random.uniform(49.0, 50.0+(50*pump.work_coef))

    return {
        "petrol_pressure_input": petrol_pressure_input,
        "petrol_pressure_output": petrol_pressure_output,
        "front_bearing_pump_temperature": front_bearing_pump_temperature,
        "rear_bearing_pump_temperature": rear_bearing_pump_temperature,
    }


async def run_pump(pump_name: str, pump: Pump, period_seconds: float) -> None:
    pump.start_pump()
    vibration_anomaly_counter = 0
    temperature_anomaly_counter = 0
    max_anomalies_before_stop = 5

    while pump.state == "on":
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
            f"vib_front_vert={pump.front_bearing_vertical_vibration:.3f}, vib_front_horiz={pump.front_bearing_horizontal_vibration:.3f}, "
            f"vib_rear_vert={pump.rear_bearing_vertical_vibration:.3f}, vib_rear_horiz={pump.rear_bearing_horizontal_vibration:.3f}, vib_rear_axial={pump.rear_bearing_axial_vibration:.3f}, "
            f"kpd={pump.kpd_value:.1f}%",
        )

        vibration_vertical_anomaly = (
            pump.rear_bearing_vertical_vibration > 1.14
            or pump.front_bearing_vertical_vibration > 1.14
        )
        vibration_horizontal_anomaly = (
            pump.rear_bearing_horizontal_vibration > 1.14
            or pump.front_bearing_horizontal_vibration > 1.14
        )
        vibration_axial_anomaly = (
            pump.rear_bearing_axial_vibration > 0.99
        )
        temperature_anomaly = (
            values["front_bearing_pump_temperature"] > 49.8
            or values["rear_bearing_pump_temperature"] > 49.8
        )

        if (pump.rear_bearing_vertical_vibration > 2
            or pump.front_bearing_vertical_vibration > 2):
            print(
                f"{pump_name}: TOO HIGH VIBRATION anomaly detected "
                f"Stopping the pump!"
            )
            pump.stop_pump()
            break

        if (pump.rear_bearing_horizontal_vibration > 2
            or pump.front_bearing_horizontal_vibration > 2):
            print(
                f"{pump_name}: TOO HIGH VIBRATION anomaly detected "
                f"Stopping the pump!"
            )
            pump.stop_pump()
            break

        if (pump.rear_bearing_axial_vibration > 2):
            print(
                f"{pump_name}: TOO HIGH VIBRATION anomaly detected "
                f"Stopping the pump!"
            )
            pump.stop_pump()
            break

        if vibration_vertical_anomaly or vibration_horizontal_anomaly or vibration_axial_anomaly:
            vibration_anomaly_counter += 1
            print(
                f"{pump_name}: VIBRATION anomaly detected "
                f"(count={vibration_anomaly_counter})"
            )
        elif vibration_anomaly_counter > 0:
            vibration_anomaly_counter = 0

        if temperature_anomaly:
            temperature_anomaly_counter += 1
            print(
                f"{pump_name}: TEMPERATURE anomaly detected "
                f"(count={temperature_anomaly_counter})"
            )
        elif temperature_anomaly_counter > 0:
            temperature_anomaly_counter = 0

        print(
            f"{pump_name}: counters -> "
            f"vibration={vibration_anomaly_counter}, "
            f"temperature={temperature_anomaly_counter}"
        )

        if (
            vibration_anomaly_counter >= max_anomalies_before_stop
            or temperature_anomaly_counter >= max_anomalies_before_stop
        ):
            print(f"{pump_name}: Too many anomalies! Stopping the pump.")
            pump.stop_pump()
            break
    
            
        await asyncio.sleep(period_seconds)

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
    
    all_tasks = pump_tasks
    
    try:
        await asyncio.gather(*all_tasks)
    except asyncio.CancelledError:
        pass
    finally:
        for task in all_tasks:
            task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user")