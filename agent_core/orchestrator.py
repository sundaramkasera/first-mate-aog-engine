import os
import cohere
from agent_core.tools import TOOL_FUNCTIONS

# Initialize Cohere Client
co = cohere.Client(os.environ.get("COHERE_API_KEY", "YOUR_API_KEY_HERE"))

# Define the tools schema for the LLM
agent_tools = [
    {
        "name": "run_coral_query",
        "description": (
            "Executes a SQL query against the enterprise database. "
            "CRITICAL SCHEMA MAP - YOU MUST ONLY USE THESE COLUMNS:\n"
            "- aog_data.codex (Columns: fault_code, system, required_part, compliance_action, estimated_repair_hours)\n"
            "- aog_data.inventory (Columns: part_id, station, available_stock, replenishment_days, bin_location)\n"
            "- aog_data.fleet (Columns: tail_number, airframe, current_location, status, crew_on_duty)\n"
            "Use this to find parts, check stock delays, and locate backup aircraft (status='IDLE')."
        ),
        "parameter_definitions": {
            "sql_query": {
                "description": "The exact SQL query to execute. Do not guess column names.",
                "type": "str",
                "required": True
            }
        }
    },
    {
        "name": "check_live_aviation_weather",
        "description": "Checks live weather conditions for a specific Indian airport hub (e.g., DEL, BOM, BLR).",
        "parameter_definitions": {
            "airport_code": {
                "description": "The 3-letter IATA airport code.",
                "type": "str",
                "required": True
            }
        }
    }
]

system_prompt = (
    "You are The First Mate, an elite AOG mitigation and logistics agent. "
    "Step 1: Query aog_data.codex using the fault_code to find the required part and estimated_repair_hours. "
    "Step 2: Check aog_data.inventory for that part at the grounded aircraft's location. "
    "Step 3: IF stock=0, search aog_data.fleet for an IDLE backup aircraft at the same hub (tail_number != '<grounded_tail>'). "
    "CRITICAL ESCALATION: If zero backup aircraft are available, state manual fleet escalation is required and skip to Step 5. "
    "Step 4: Check live aviation weather for the hub. "
    "FINAL OUTPUT RULES: "
    "1. Synthesize all findings into a single, continuous, highly detailed ATC-style paragraph. "
    "2. DO NOT use any Markdown formatting, bolding, bullet points, or hash symbols (#). "
    "3. DO NOT use line breaks or newlines. "
    "4. Explicitly state the grounded tail, required part, inventory delay, the backup tail number, and the weather."
)

def mitigate_aog(tail_number: str, fault_code: str):
    """
    Executes the multi-step reasoning loop to resolve an AOG event.
    """
    user_message = f"CRITICAL AOG ALERT: Aircraft {tail_number} has reported fault code {fault_code}. Initialize mitigation protocol."
    
    print(f"\n--- INITIATING FIRST MATE PROTOCOL FOR {tail_number} ---")
    
    # Initial call to the LLM
    response = co.chat(
        message=user_message,
        preamble=system_prompt,
        tools=agent_tools,
        model="command-r-plus-08-2024"
    )
    
    # Tool execution loop with Circuit Breaker
    max_steps = 8
    step_count = 0
    
    if not response.tool_calls:
        yield response.text
        return

    while response.tool_calls and step_count < max_steps:
        step_count += 1
        tool_results = []
        for tool_call in response.tool_calls:
            print(f"\n[*] Agent executing tool: {tool_call.name}")
            print(f"    Parameters: {tool_call.parameters}")
            
            # Execute the actual Python function
            func = TOOL_FUNCTIONS.get(tool_call.name)
            if func:
                result = func(**tool_call.parameters)
                tool_results.append({"call": tool_call, "outputs": [{"result": result}]})
                print(f"    -> Result: {result.strip()}")
        
        # Send results back to the LLM
        stream = co.chat_stream(
            message="",
            chat_history=response.chat_history,
            preamble=system_prompt,
            tools=agent_tools,
            tool_results=tool_results,
            model="command-r-plus-08-2024"
        )
        
        for event in stream:
            if event.event_type == "text-generation":
                yield event.text
            elif event.event_type == "stream-end":
                response = event.response
        
    if step_count >= max_steps:
        error_msg = "⚠️ CIRCUIT BREAKER TRIPPED: Agent exceeded maximum tool calls. Manual escalation required."
        print(f"\n{error_msg}")
        yield error_msg
    
    print("\n--- FINAL RECOVERY DIRECTIVE ---")
    print(response.text)

if __name__ == "__main__":
    # Test execution for the terminal
    mitigate_aog("VT-772ZA", "ERR-772")
