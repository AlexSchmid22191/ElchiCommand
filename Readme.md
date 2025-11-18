# ElchiCommander

Version: 1.1
Date: 2025-11-16
Author: Alex Schmid
Organization: TU Wien

## Description

ElchiCommander is a command line tool for interfacing with experiment control hardware, such as temperature controlelrs,
gas flow controllers, relays, or multiplexers.
It executes actions predefined in a configuration file.

## Usage

### Installation

Run EC_Installer.exe to install ElchiCommander.

### Configuration

Before starting an experiment, you have to specify the hardware used in the experiment, as well as any actions that will
be executed during the experiment.
This is done via a configuration file stored in the user config directory.
On Windows, this is typically `C:\Users\<username>\AppData\Roaming\Elchworks\ElchiCommander\config.yaml.`
ElchiCommander comes with two .bat scripts which can be used to create example configuration files.

This configuration file consists of two main sections: devices and actions.
The devices section specifies the devices (e.g., heaters, flow controllers, etc.) to be controlled during the
experiment,
while actions specify specific actions to be executed using one more or more of those devices (e.g., heating to a
certain temperature, or setting a specific flow rate).

A detailed specification of the configuration file format can be found below.

#### ElchiCreator Wizard
ElchiCreator is an interactive command line wizard that helps you in creating a configuration file step-by-step. It is especially suited for creating (nested) cycles, e.g. temeprature and trigger or gas and temperature.
It is found in the ElchiCommander installation directory.

### Running

To execute an action, run `ElchiCommander.exe action_id`, where action_id is the id of the action to be executed.
This is typically done from within the measurement program (DetaChem or EC-Lab), but can also be done from the command
line terminal.
When running from DetaChem, the action_ids to be executed are specified via the free variable list in the DetaChem
experiment configuration.
DetaChem then calls ElchiCommander with the next entry in the list on each iteration of the measurement loop.
In EC-Lab, the action_id can be specified in the experiment configuration using the ExtApp technique.

### Error handling

A successful execution of ElchiCommander ends with the termination of the process, thus handing back the control flow
to the calling program (DetaChem or EC-Lab).
If an error occurs during execution, ElchiCommander will print an error message to the console and wait for the user to
confirm before terminating.
Caution: EC-Lab by default has a timeout of 15 minutes for the execution of ElchiCommander, after which it will
force-terminate ElchiCommander.
This can be changed in the EC-Lab.ini file.

### Logging

On every call of ElchiCommander, a log file is created in the user config directory.
This log file contains information about the executed actions, their success and failure, as well as any error messages
that may have occurred.
For every day, a new log file is created to keep the file size manageable.
Specifically, for the set_temperature action, a separate log file is created that only stores time, temperature
setpoint, and stabilized temperature, to allow easier parsing for data processing.

## Configuration file specification

The configuration file is a YAML file.
Therefore, indentation is significant.
Two spaces per hierarchy level are used for indentation.
The installation comes with .bat scripts that can be used to (re)generate example configuration files.

### Devices

The devices section specifies all devices to be controlled during the experiment.
Each device is specified by a unique id, followed by a list of key, value paris.
The necessary keys are:

#### type

The type of the device. Must be one of:

- heater
- temp_sensor
- flow_controller
- triggerbox
- multiplexer

#### device

The specific device to be used. Must match the device type:

- heater:
    - Eurotherm3216
    - Eurotherm2408
    - Omega Pt
    - Jumo Quantrol
    - Elch Heater Controller
    - Elch Laser Control
    - Test Controller
    - Nice Test Controller
- temp_sensor:
    - Thermolino
    - Pyrometer
    - Thermoplatino
    - Keithly2000
    - Test Sensor
- flow_controller:
    - Ventolino
    - Aera ROD-4
    - Test MFC
- triggerbox:
    - Omni Trigger
    - Valvolino
    - Test Trigger
- multiplexer:
    - Omniplex
    - Test Multiplexer

Note: Test devices are stubs that do not communicate with anything and only print a message to the console when a
command is to be executed. They can be used for testing.

#### port:

The COM port to be used for communication with the device.
Must be a COM port that is actually available on the system.
Alternatively, COMXY may be used for testing.

### Actions

The actions section specifies all actions to be executed during the experiment.
Each action is specified by a unique id, followed by a list of key, value pairs.
All actions must include the type key, which specifies the type of the action.
The following types are currently supported:

#### set_temp_blind

Set the temperature setpoint of a heater to a given value.
Required fields:

- type: set_temp_blind
- heater: The id of the heater to be controlled, must be defined in the device section.
- t_set: The temperature setpoint in degree Celsius to be set. Must be between -200 and 1500.

#### set_temp

Set the temperature-setpoint of a heater to a given value and wait till the temperature of a sensor has stabilized.
Required fields:

- type: set_temp
- heater: The id of the heater to be controlled, must be defined in the device section.
- temp_sensor: The id of the temperature sensor to be used for monitoring. Must be defined in the device section.
- t_set: The temperature setpoint in degree Celsius to be set. Must be between -200 and 1500.
- delta_time: The time in seconds for which the temperature of the sensor must change less than specified by delta_temp.
  Must be between 1 and 1000000.
- delta_temp: The maximum temperature change in degree Celsius that is allowed. Must be between 0.01 and 100.
- time_res: The time resolution in seconds for the temperature measurement. Must be between 1 and 100.

#### set_flow

Set the flow rate of a flow controller to a given value.
Required fields:

- type: set_flow
- flow_controller: The id of the flow controller to be controlled. Must be defined in the device section.
- flow_1: The flow rate in % of the full range to be set for channel 1; must be between 0 and 100.
- flow_2: The flow rate in % of the full range to be set for channel 2; must be between 0 and 100.
- flow_3: The flow rate in % of the full range to be set for channel 3; must be between 0 and 100.
- flow_4: The flow rate in % of the full range to be set for channel 4; must be between 0 and 100.

#### trigger

Set the four relays of a triggerbox or the four valves of a valve controller to a given value.
Required fields:

- type: trigger
- triggerbox: The id of the triggerbox to be controlled. Must be defined in the device section.
- state_1: State of valve or relay 1. Must be either 0 or 1.
- state_2: State of valve or relay 2. Must be either 0 or 1.
- state_3: State of valve or relay 3. Must be either 0 or 1.
- state_4: State of valve or relay 4. Must be either 0 or 1.

#### multiplexer

Set the 16 relays of a multiplexer to a given value.
Required fields:

- type: multiplexer
- multiplexer: The id of the multiplexer to be controlled. Must be defined in the device section.
- state_L1R1: State of valve or relay connecting port L1 to R1. Must be either 0 or 1.
- state_L2R1: State of valve or relay connecting port L2 to R1. Must be either 0 or 1.
- state_L3R1: State of valve or relay connecting port L3 to R1. Must be either 0 or 1.
- state_L4R1: State of valve or relay connecting port L4 to R1. Must be either 0 or 1.
- state_L1R2: State of valve or relay connecting port L1 to R2. Must be either 0 or 1.
- state_L2R2: State of valve or relay connecting port L2 to R2. Must be either 0 or 1.
- state_L3R2: State of valve or relay connecting port L3 to R2. Must be either 0 or 1.
- state_L4R2: State of valve or relay connecting port L4 to R2. Must be either 0 or 1.
- state_L1R3: State of valve or relay connecting port L1 to R3. Must be either 0 or 1.
- state_L2R3: State of valve or relay connecting port L2 to R3. Must be either 0 or 1.
- state_L3R3: State of valve or relay connecting port L3 to R3. Must be either 0 or 1.
- state_L4R3: State of valve or relay connecting port L4 to R3. Must be either 0 or 1.
- state_L1R4: State of valve or relay connecting port L1 to R4. Must be either 0 or 1.
- state_L2R4: State of valve or relay connecting port L2 to R4. Must be either 0 or 1.
- state_L3R4: State of valve or relay connecting port L3 to R4. Must be either 0 or 1.
- state_L4R4: State of valve or relay connecting port L4 to R4. Must be either 0 or 1.

#### iterate_list

Iterate list is a meta-action consisting of a list of actions which are consecutively executed on each execution of the
iterate_list action.
Required fields:

- type: iterate_list
- action_ids: A list of action_ids to be executed. Each action id must be defined in the actions section.
- processed_actions: A list of action ids that have been processed. This list is updated on each execution of the
  iterate_list action by ElchiCommander. At the start of the experiment it should be an empty list.
