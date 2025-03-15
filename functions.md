# Functions

## Overview
This document outlines the functions of the Defi Oracle Meta Deployer project.

## Functions

1. **run_command(cmd)**
   - Runs a shell command and returns the output.
   - Logs the command execution and handles errors.

2. **create_resource_group()**
   - Executes the Azure CLI command to create a resource group.
   - Uses the `run_command` function to execute the command.

3. **deploy_vm()**
   - Executes the Azure CLI command to deploy a virtual machine.
   - Uses the `run_command` function to execute the command.

4. **deploy_via_rest_api()**
   - Demonstrates a REST API call to Azure Resource Manager for deployment.
   - Constructs the API URL and payload.
   - Uses the `requests` library to make the API call.
   - Handles authentication and error responses.

5. **index()**
   - Renders the main HTML interface.

6. **execute_action()**
   - Handles the form submission from the HTML interface.
   - Calls the appropriate function based on the selected action.
   - Renders the result in the HTML interface.

## Future Enhancements

1. **Modularization**
   - Further break down functions into smaller, reusable components.

2. **Detailed Logging**
   - Enhance logging with more detailed information and context.

3. **Error Handling**
   - Improve error handling with more specific error messages and recovery options.
