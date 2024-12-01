# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 22:08:05 2024

@author: DELL
"""

import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Database connection
conn = sqlite3.connect("blood_donation.db")
cursor = conn.cursor()

# Create tables
def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        blood_group TEXT NOT NULL,
        location TEXT NOT NULL,
        contact_info TEXT NOT NULL,
        last_donation_date DATE
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recipients (
        recipient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        location TEXT NOT NULL,
        contact_info TEXT NOT NULL,
        request_date DATE
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blood_banks (
        bank_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        contact_info TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        available_units INTEGER DEFAULT 0
    );
    """)
    conn.commit()
   
# Initialize database
init_db()

# Streamlit app
st.title("Blood Donation Management System")

# Add Donor
if st.sidebar.button("Register as Donor"):
    with st.form("Donor Form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=18, max_value=65)
        blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        location = st.text_input("Location")
        contact_info = st.text_input("Contact Info")
        last_donation_date = st.date_input("Last Donation Date")
        submitted = st.form_submit_button("Submit")

        if submitted:
            cursor.execute("INSERT INTO donors (name, age, blood_group, location, contact_info, last_donation_date) VALUES (?, ?, ?, ?, ?, ?)",
                           (name, age, blood_group, location, contact_info, last_donation_date))
            conn.commit()
            st.success("Donor Registered Successfully!")

# View Donors
if st.sidebar.button("View Donors"):
    donors = pd.read_sql_query("SELECT * FROM donors", conn)
    st.dataframe(donors)

# Add Recipient
if st.sidebar.button("Request Blood"):
    with st.form("Recipient Form"):
        name = st.text_input("Name")
        blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        location = st.text_input("Location")
        contact_info = st.text_input("Contact Info")
        request_date = st.date_input("Request Date")
        submitted = st.form_submit_button("Submit")

        if submitted:
            cursor.execute("INSERT INTO recipients (name, blood_group, location, contact_info, request_date) VALUES (?, ?, ?, ?, ?)",
                           (name, blood_group, location, contact_info, request_date))
            conn.commit()
            st.success("Request Submitted Successfully!")

# Match Donors
if st.sidebar.button("Find Compatible Donors"):
    with st.form("Find Donor"):
        blood_group = st.selectbox("Recipient Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        location = st.text_input("Recipient Location")
        submitted = st.form_submit_button("Search")

        if submitted:
            compatible_groups = {
                "A+": ["A+", "A-", "O+", "O-"],
                "B+": ["B+", "B-", "O+", "O-"],
                "O+": ["O+", "O-"],
                "AB+": ["A+", "B+", "AB+", "O+", "A-", "B-", "AB-", "O-"],
                # Add other compatibilities
            }
            results = pd.read_sql_query(f"""
            SELECT * FROM donors WHERE blood_group IN ({', '.join(['?'] * len(compatible_groups[blood_group]))}) AND location = ?
            """, conn, params=(compatible_groups[blood_group] + [location]))
            st.dataframe(results)

conn.close()


