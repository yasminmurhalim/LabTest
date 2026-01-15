import streamlit as st
import operator
from typing import List, Dict, Any, Tuple

comparisons = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


defaults_conditions: List[Dict[str, Any]] = [
  {
    "name": "Windows open \u2192 turn AC off",
    "priority": 100,
    "conditions": [
      ["windows_open", "==", True]
    ],
    "action": {
      "ac_mode": "OFF",
      "fan_speed": "LOW",
      "setpoint": None,
      "reason": "Windows are open"
    }
  },
  {
    "name": "No one home \u2192 eco mode",
    "priority": 90,
    "conditions": [
      ["occupancy", "==", "EMPTY"],
      ["temperature", ">=", 24]
    ],
    "action": {
      "ac_mode": "ECO",
      "fan_speed": "LOW",
      "setpoint": 27,
      "reason": "Home empty; save energy"
    }
  },
  {
    "name": "Hot & humid (occupied) \u2192 cool strong",
    "priority": 80,
    "conditions": [
      ["occupancy", "==", "OCCUPIED"],
      ["temperature", ">=", 30],
      ["humidity", ">=", 70]
    ],
    "action": {
      "ac_mode": "COOL",
      "fan_speed": "HIGH",
      "setpoint": 23,
      "reason": "Hot and humid"
    }
  },
  {
    "name": "Hot (occupied) \u2192 cool",
    "priority": 70,
    "conditions": [
      ["occupancy", "==", "OCCUPIED"],
      ["temperature", ">=", 28]
    ],
    "action": {
      "ac_mode": "COOL",
      "fan_speed": "MEDIUM",
      "setpoint": 24,
      "reason": "Temperature high"
    }
  },
  {
    "name": "Slightly warm (occupied) \u2192 gentle cool",
    "priority": 60,
    "conditions": [
      ["occupancy", "==", "OCCUPIED"],
      ["temperature", ">=", 26],
      ["temperature", "<", 28]
    ],
    "action": {
      "ac_mode": "COOL",
      "fan_speed": "LOW",
      "setpoint": 25,
      "reason": "Slightly warm"
    }
  },
  {
    "name": "Night (occupied) \u2192 sleep mode",
    "priority": 75,
    "conditions": [
      ["occupancy", "==", "OCCUPIED"],
      ["time_of_day", "==", "NIGHT"],
      ["temperature", ">=", 26]
    ],
    "action": {
      "ac_mode": "SLEEP",
      "fan_speed": "LOW",
      "setpoint": 26,
      "reason": "Night comfort"
    }
  },
  {
    "name": "Too cold \u2192 turn off",
    "priority": 85,
    "conditions": [
      ["temperature", "<=", 22]
    ],
    "action": {
      "ac_mode": "OFF",
      "fan_speed": "LOW",
      "setpoint": None,
      "reason": "Already cold"
    }
  }
]


#logic 

def validate_condition(facts: Dict[str, Any], condition: List[Any]) -> bool:
    field, op, value = condition
    
    if field not in facts:
        return False
    if op not in comparisons:
        return False
    return comparisons[op](facts[field], value)

def check_rule_match(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    
    return all(validate_condition(facts, cond) for cond in rule["conditions"])

def execute_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    triggered_rules = [rule for rule in rules if check_rule_match(facts, rule)]
    
    if not triggered_rules:
      
        return {"ac_mode": "IDLE", "fan_speed": "LOW", "setpoint": None, "reason": "No matching rules"}, []
    
   
    sorted_rules = sorted(triggered_rules, key=lambda r: r["priority"], reverse=True)
    
    
    return sorted_rules[0]["action"], sorted_rules

# streamlit ui
st.set_page_config(page_title="AC Controller Pro", layout="wide")

st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Rule based smart home air conditioner control")
st.markdown("---")

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.subheader("Environment Sensors")
    
    temp = st.slider("Ambient Temperature (°C)", 10, 45, 22)
    humid = st.slider("Relative Humidity (%)", 0, 100, 46)
    
    st.markdown("---")
    st.subheader("Home State")
    occ = st.radio("Occupancy Status", ["OCCUPIED", "EMPTY"], horizontal=True)
    
    tod_options = ["MORNING", "AFTERNOON", "EVENING", "NIGHT"]
    tod = st.select_slider("Current Period", options=tod_options, value="NIGHT")
    
    win = st.toggle("Windows / Ventilation Open", value=False)
    
    run_btn = st.button("Apply Settings & Sync AC", use_container_width=True, type="primary")

facts_data = {
    "temperature": temp,
    "humidity": humid,
    "occupancy": occ,
    "time_of_day": tod,
    "windows_open": win
}

with col_out:
    if run_btn:
        action, matched = execute_rules(facts_data, defaults_conditions)
        
        st.subheader("System Output")
        
        m1, m2, m3 = st.columns(3)
       
        with m1: st.metric("Mode", action.get('ac_mode', 'ERR'))
        with m2: st.metric("Fan", action.get('fan_speed', 'ERR'))
        with m3: st.metric("Target", f"{action['setpoint']}°C" if action['setpoint'] else "N/A")
        
        with st.container(border=True):
            st.markdown(f"**Decision Logic:** {action.get('reason', 'Unknown')}")
        
        with st.expander("View Logic Trace"):
            st.write("Sensor Data Snapshot")
            st.json(facts_data)
            
            st.write("Rule Processing Queue")
            if matched:
                for i, r in enumerate(matched):
                    symbol = "Yes" if i == 0 else "No"
                    
                    st.write(f"{symbol} **{r['name']}**")
                    st.caption(f"Priority Score: {r['priority']}")
            else:
                st.warning("No logic rules triggered.")
    else:
        st.info("Adjust the sensors on the left and click **Apply Settings** to simulate the AC logic.")

st.markdown("---")
st.caption("rule based AC control systems")