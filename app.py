import streamlit as st
import pandas as pd
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="SHRIRAM Logistics Portal", layout="wide")

# --- MOCK DATABASE (In-memory for demo) ---
if 'trips' not in st.session_state:
    st.session_state.trips = []
if 'bids' not in st.session_state:
    st.session_state.bids = []

st.title("🚛 SHRIRAM Logistics: Backhaul Marketplace")
st.sidebar.title("Navigation")
role = st.sidebar.radio("Select Your Role:", ["Sidharthan (Truck Owner)", "Client (Bidder)", "Shriram (Admin)"])

# --- PANEL 1: SIDHARTHAN (Truck Owner) ---
if role == "Sidharthan (Truck Owner)":
    st.header("Post Available Return Trip")
    with st.form("truck_entry"):
        col1, col2 = st.columns(2)
        truck_no = col1.text_input("Truck Reg No.")
        volume = col1.number_input("Total Volume Capacity (cu.ft)", min_value=100)
        floor_price = col2.number_input("Minimum Floor Price (₹)", min_value=1000)
        deadline = col2.date_input("Bidding Deadline")
        
        if st.form_submit_button("List Truck for Return"):
            st.session_state.trips.append({
                "id": len(st.session_state.trips) + 1,
                "truck": truck_no,
                "vol": volume,
                "price": floor_price,
                "deadline": deadline,
                "status": "Open"
            })
            st.success(f"Truck {truck_no} listed successfully!")

# --- PANEL 2: CLIENT (Bidders like MADHU) ---
elif role == "Client (Bidder)":
    st.header("Available Trucks (Coimbatore to Chennai)")
    if not st.session_state.trips:
        st.info("No trucks available for bidding yet.")
    else:
        for trip in st.session_state.trips:
            with st.expander(f"Truck: {trip['truck']} | Space: {trip['vol']} cu.ft"):
                st.write(f"Min Bid: ₹{trip['price']}")
                with st.form(f"bid_form_{trip['id']}"):
                    c_name = st.text_input("Company Name")
                    g_type = st.text_input("Type of Goods")
                    req_vol = st.number_input("Required Volume (cu.ft)")
                    bid_amt = st.number_input("Your Bid Price (₹)")
                    
                    if st.form_submit_button("Submit Blind Tender"):
                        st.session_state.bids.append({
                            "trip_id": trip['id'],
                            "client": c_name,
                            "goods": g_type,
                            "vol": req_vol,
                            "amount": bid_amt,
                            "status": "Pending"
                        })
                        st.success("Bid submitted privately to SHRIRAM.")

# --- PANEL 3: SHRIRAM (Admin Dashboard) ---
elif role == "Shriram (Admin)":
    st.header("Admin Control: Tender Management")
    
    for trip in st.session_state.trips:
        st.subheader(f"Managing Truck: {trip['truck']} (Cap: {trip['vol']} cu.ft)")
        
        # Filter bids for this specific truck
        truck_bids = [b for b in st.session_state.bids if b['trip_id'] == trip['id']]
        
        if truck_bids:
            df = pd.DataFrame(truck_bids)
            st.table(df) # Shows all bids including secret prices
            
            selected_indices = st.multiselect(f"Select companies to load on {trip['truck']}:", 
                                             range(len(truck_bids)), 
                                             format_func=lambda x: f"{truck_bids[x]['client']} - ₹{truck_bids[x]['amount']}")
            
            if st.button(f"Finalize Loading for {trip['truck']}"):
                total_load = sum([truck_bids[i]['vol'] for i in selected_indices])
                if total_load > trip['vol']:
                    st.error(f"Overloaded! Total volume {total_load} exceeds truck capacity {trip['vol']}.")
                else:
                    st.success(f"Selection Finalized! Total Revenue: ₹{sum([truck_bids[i]['amount'] for i in selected_indices])}")
        else:
            st.write("No bids received yet.")
