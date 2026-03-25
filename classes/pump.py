from utils.utils import FRONT_BEARING_VERTICAL_VIBRATION_COEFFICIENT, REAR_BEARING_AVG_TEMPERATURE, REAR_BEARING_VERTICAL_VIBRATION_COEFFICIENT, REAR_BEARING_VERTICAL_VIBRATION_COEFFICIENT, STANDART_RPM

class Pump:
    state = "off"

    def __init__(self, petrol_pressure_input, petrol_pressure_output, front_bearing_pump_temperature, rear_bearing_pump_temperature, rpm=STANDART_RPM):
        self.front_bearing_pump_temperature = front_bearing_pump_temperature
        self.rear_bearing_pump_temperature = rear_bearing_pump_temperature
        self.petrol_pressure_input = petrol_pressure_input
        self.petrol_pressure_output = petrol_pressure_output
        self.rpm = rpm
        self.work_coef = 0.01
        self.rear_bearing_vertical_vibration = self.calculate_rpm_temperature_correlation(0.56, self.rear_bearing_pump_temperature, REAR_BEARING_AVG_TEMPERATURE, REAR_BEARING_VERTICAL_VIBRATION_COEFFICIENT, self.rpm, self.work_coef)
        self.rear_bearing_horizontal_vibration = self.calculate_rpm_temperature_correlation(0.44, self.rear_bearing_pump_temperature, REAR_BEARING_AVG_TEMPERATURE, 0, self.rpm, self.work_coef)
        self.rear_bearing_axial_vibration = self.calculate_rpm_temperature_correlation(0.6, self.rear_bearing_pump_temperature, REAR_BEARING_AVG_TEMPERATURE, 0, self.rpm, self.work_coef)
        self.front_bearing_vertical_vibration = self.calculate_rpm_temperature_correlation(0.56, self.front_bearing_pump_temperature, REAR_BEARING_AVG_TEMPERATURE, FRONT_BEARING_VERTICAL_VIBRATION_COEFFICIENT, self.rpm, self.work_coef)
        self.front_bearing_horizontal_vibration = self.calculate_rpm_temperature_correlation(0.44, self.front_bearing_pump_temperature, REAR_BEARING_AVG_TEMPERATURE, 0, self.rpm, self.work_coef)
        self.anomaly_active = False
        #self.vertical_front_bearing_pump_vibration = vertical_front_bearing_pump_vibration
        #self.horizontal_front_bearing_pump_vibration = horizontal_front_bearing_pump_vibration
        #self.vertical_rear_bearing_pump_vibration = vertical_rear_bearing_pump_vibration
        #self.horizontal_rear_bearing_pump_vibration = horizontal_rear_bearing_pump_vibration
        #self.axial_rear_bearing_pump_vibration = axial_rear_bearing_pump_vibration

    def start_pump(self):
        self.state = "on"

    def stop_pump(self):
        self.state = "off"

    def trigger_anomaly(self):
        """Enable anomaly mode for this pump."""
        self.anomaly_active = True

    def clear_anomaly(self):
        """Disable anomaly mode for this pump."""
        self.anomaly_active = False

    
    def calculate_rpm_temperature_correlation(base_vibration, current_temperature, avg_temperature, correlation_coef, current_rpm, work_coef):
        return (base_vibration + (correlation_coef * (current_temperature - avg_temperature))) * (current_rpm / STANDART_RPM) * (1 + work_coef)

    def iteration(self, petrol_pressure_input, petrol_pressure_output, front_bearing_pump_temperature, rear_bearing_pump_temperature):
        self.petrol_pressure_input = petrol_pressure_input
        self.petrol_pressure_output = petrol_pressure_output
        self.front_bearing_pump_temperature = front_bearing_pump_temperature
        self.rear_bearing_pump_temperature = rear_bearing_pump_temperature
        self.work_coef += 0.01

        #self.frame_temperature = frame_temperature
        #self.front_bearing_engine_temperature = front_bearing_engine_temperature
        #self.rear_bearing_engine_temperature = rear_bearing_engine_temperature
        #self.stator_temperature = stator_temperature
        #self.rotor_temperature = rotor_temperature
        #self.hot_air_in_engine_frame_temperature = hot_air_in_engine_frame_temperature
        #self.cold_air_in_engine_frame_temperature = cold_air_in_engine_frame_temperature