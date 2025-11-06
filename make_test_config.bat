@echo off
setlocal

rem Target: %APPDATA%\ElchWorks\ElchiCommander\config.yaml
set "CFGDIR=%APPDATA%\ElchWorks\ElchiCommander"
set "CFGFILE=%CFGDIR%\config.yaml"

if not exist "%CFGDIR%" mkdir "%CFGDIR%"

> "%CFGFILE%" (
  echo # Experiment configuration file for ElchiCommand
  echo # v1.0
  echo.
  echo # ---------------------------------------------------------------------------------------------------------------
  echo # Definition of available devices
  echo # Change the device type and port to match your setup or add new devices as explained in the coLab
  echo # ATTENTION: THE INDENTATION IS IMPORTANT!
  echo # TWO SPACES BEFORRE A DEVICE_ID ARE REQUIRED!
  echo # FOUR SPACES BEFORE A PROPERRTY OF A DEVICE ARE REQUIRED!
  echo.
  echo devices:
  echo   oven_1:
  echo     type: heater
  echo     device: Nice Test Controller
  echo     port: COMXY
  echo   temp_sensor_1:
  echo     type: temp_sensor
  echo     device: Test Sensor
  echo     port: COMXY
  echo   gas_ctrl_1:
  echo     type: flow_controller
  echo     device: Test MFC
  echo     port: COMXY
  echo   triggerbox_1:
  echo     type: triggerbox
  echo     device: Test Trigger
  echo     port: COMXY
  echo   multiplexer_1:
  echo     type: multiplexer
  echo     device: Test Multiplexer
  echo     port: COMXY
  echo.
  echo # ---------------------------------------------------------------------------------------------------------------
  echo # Definition of available actions to be performed as part of the experiment
  echo # For a detailed description of the actions, see the documentation in the colab
  echo # Edit these example actions to suit your needs or add new actions
  echo # Each action is identified by a unique number, is defiend by a type and contains one or more devices from the
  echo # definition above as well as one or more parameters depending on the action type
  echo # On each execution of ElchiCommand the action corresponding to the id given to ElchiCommand is executed
  echo # ATTENTION: THE INDENTATION IS IMPORTANT!
  echo # TWO SPACES BEFORRE AN ID ARE REQUIRED!
  echo # FOUR SPACES BEFORE A PROPERRTY OF AN ID ARE REQUIRED!
  echo.
  echo actions:
  echo   1:
  echo     type: set_temp
  echo     heater: oven_1
  echo     temp_sensor: temp_sensor_1
  echo     t_set: 500
  echo     delta_time: 900
  echo     delta_temp: 0.5
  echo     time_res: 5
  echo   2:
  echo     type: set_temp_blind
  echo     heater: oven_1
  echo     t_set: 500
  echo   3:
  echo     type: gas_ctrl
  echo     flow_controller: gas_ctrl_1
  echo     flow_1: 0.0
  echo     flow_2: 0.0
  echo     flow_3: 0.0
  echo     flow_4: 0.0
  echo   4:
  echo     type: trigger
  echo     triggerbox: triggerbox_1
  echo     state_1: 0
  echo     state_2: 0
  echo     state_3: 0
  echo     state_4: 0
  echo   5:
  echo     type: multiplexer
  echo     multiplexer: multiplexer_1
  echo     state_L1R1: 0
  echo     state_L2R1: 0
  echo     state_L3R1: 0
  echo     state_L4R1: 0
  echo     state_L1R2: 0
  echo     state_L2R2: 0
  echo     state_L3R2: 0
  echo     state_L4R2: 0
  echo     state_L1R3: 0
  echo     state_L2R3: 0
  echo     state_L3R3: 0
  echo     state_L4R3: 0
  echo     state_L1R4: 0
  echo     state_L2R4: 0
  echo     state_L3R4: 0
  echo     state_L4R4: 0
  echo   6:
  echo    type: iterate_list
  echo    action_ids: [4, 4, 4, 4, 4]
  echo    processed_actions: []
  echo.
  echo # ---------------------------------------------------------------------------------------------------------------
)

echo Created "%CFGFILE%"
echo.
set /p "=Press Enter to exit..." <nul & pause >nul
endlocal