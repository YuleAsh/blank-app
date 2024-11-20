import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Sample data generation (50 records) with both disputed and undisputed data
def generate_sample_data():
    np.random.seed(42)
    
    # We will create 12 months of data and ensure at least 4 carriers per month
    months = pd.date_range(start="2024-01-01", periods=12, freq='M').strftime('%Y-%m').tolist()
    carriers = [f'Carrier {i}' for i in range(1, 11)]  # 10 unique carriers
    
    data = []
    
    # Generate data ensuring at least 3-4 carriers for each month
    for month in months:
        for carrier in carriers:
            # Simulate invoice amount (in USD) and decide if it's disputed or not
            invoice_amount = np.random.uniform(1000, 5000)
            is_disputed = np.random.rand() < 0.2  # 20% chance that the invoice is disputed
            
            if is_disputed:
                disputed_amount = np.random.uniform(0, invoice_amount * 0.3)  # Dispute amount between 0% and 30% of invoice
            else:
                disputed_amount = 0  # No dispute if undisputed
            
            data.append({
                'Carrier Name': carrier,
                'Invoice Amount (USD)': invoice_amount,
                'Disputed Amount (USD)': disputed_amount,
                'Reconciliation Status': np.random.choice(['Pending', 'Completed', 'In Progress']),
                'Dispute Type': np.random.choice(['Rate Dispute', 'Volume Dispute']) if is_disputed else None,
                'Settlement Status': np.random.choice(['Settled', 'Unsettled']) if is_disputed else 'Settled',
                'Invoice Month': month
            })
    
    return pd.DataFrame(data)

df = generate_sample_data()

# Set page layout to wide
st.set_page_config(layout="wide")

# Dashboard title
st.title("Telecom Billing Reconciliation Dashboard")

# Filters (Optional for drilling down)
carrier_filter = st.selectbox("Select Carrier (Optional)", options=["All"] + list(df['Carrier Name'].unique()))
month_filter = st.selectbox("Select Month (Optional)", options=["All"] + list(df['Invoice Month'].unique()))

# Applying filters (if selected) to data
filtered_df = df.copy()

if carrier_filter != "All":
    filtered_df = filtered_df[filtered_df['Carrier Name'] == carrier_filter]

if month_filter != "All":
    filtered_df = filtered_df[filtered_df['Invoice Month'] == month_filter]

# Ensure we have at least 3-4 carriers left in the filtered dataset, otherwise show a warning.
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your filters and try again.")
else:
    if month_filter != "All" and len(filtered_df['Carrier Name'].unique()) < 3:
        st.warning(f"Only {len(filtered_df['Carrier Name'].unique())} carrier(s) available for the selected month. Please adjust the filters for a better view.")
    
    # Tabs for the dashboard
    tab1, tab2, tab3, tab4 = st.tabs(["Invoice Recon", "Reconciliation Summary", "Dispute Summary", "Settlement Summary"])

    # Tab 1: Invoice Recon (Macro Overview with Scenario)
    with tab1:
        st.subheader("Invoice Reconciliation Overview")
        
        # Show full data overview
        st.write("### All Data (Unfiltered View)")
        st.dataframe(filtered_df)  # Show the filtered data (if filters are applied)

        # Scenario 1: Disputed vs Processed Amounts by Carrier
        st.write("### Disputed vs Processed Amounts by Carrier")
        if not filtered_df.empty:
            processed_vs_disputed = px.bar(filtered_df, x='Carrier Name', y=['Invoice Amount (USD)', 'Disputed Amount (USD)'], 
                                            title="Disputed vs Processed Amounts by Carrier", barmode="group")
            st.plotly_chart(processed_vs_disputed)
        else:
            st.write("No data to display for the selected filter.")

        # Scenario 2: Invoice Disputes by Month (to spot trends)
        st.write("### Invoice Disputes by Month")
        if not filtered_df.empty:
            monthly_disputes = filtered_df.groupby('Invoice Month').agg({
                'Invoice Amount (USD)': 'sum',
                'Disputed Amount (USD)': 'sum'
            }).reset_index()

            monthly_disputes_fig = px.line(monthly_disputes, x='Invoice Month', y=['Invoice Amount (USD)', 'Disputed Amount (USD)'], 
                                           title="Invoice Disputes by Month")
            st.plotly_chart(monthly_disputes_fig)
        else:
            st.write("No data to display for the selected filter.")

    # Tab 2: Reconciliation Summary (Scenario)
    with tab2:
        st.subheader("Reconciliation Summary")
        
        # Scenario 1: Carriers with Longest Pending Reconciliation
        st.write("### Carriers with Longest Pending Reconciliation")
        if not filtered_df.empty:
            pending_reconciliation = filtered_df[filtered_df['Reconciliation Status'] == 'Pending']
            pending_reconciliation_summary = pending_reconciliation.groupby('Carrier Name').agg({
                'Invoice Amount (USD)': 'sum',
                'Disputed Amount (USD)': 'sum'
            }).reset_index()

            pending_reconciliation_fig = px.bar(pending_reconciliation_summary, x='Carrier Name', 
                                                y='Invoice Amount (USD)', 
                                                title="Invoices with Pending Reconciliation by Carrier")
            st.plotly_chart(pending_reconciliation_fig)
        else:
            st.write("No data to display for the selected filter.")
        
        # Scenario 2: Reconciliation Trend by Month
        st.write("### Reconciliation Status Trend by Month")
        if not filtered_df.empty:
            reconciliation_trend = filtered_df.groupby(['Invoice Month', 'Reconciliation Status']).size().reset_index(name='Count')
            trend_fig = px.line(reconciliation_trend, x='Invoice Month', y='Count', color='Reconciliation Status', title="Reconciliation Trend Over Time")
            st.plotly_chart(trend_fig)
        else:
            st.write("No data to display for the selected filter.")

    # Tab 3: Dispute Summary (Scenario)
    with tab3:
        st.subheader("Dispute Summary")
        
        # Scenario 1: Disputes by Type and Carrier
        st.write("### Disputes by Type and Carrier")
        if not filtered_df.empty:
            dispute_type = filtered_df.groupby(['Carrier Name', 'Dispute Type']).agg({
                'Disputed Amount (USD)': 'sum'
            }).reset_index()

            dispute_type_fig = px.bar(dispute_type, x='Carrier Name', y='Disputed Amount (USD)', color='Dispute Type', 
                                      title="Disputes by Type and Carrier")
            st.plotly_chart(dispute_type_fig)
        else:
            st.write("No data to display for the selected filter.")

        # Scenario 2: Settled vs Unsettled Disputes by Carrier
        st.write("### Settled vs Unsettled Disputes by Carrier")
        if not filtered_df.empty:
            dispute_status = filtered_df.groupby(['Carrier Name', 'Settlement Status']).agg({
                'Disputed Amount (USD)': 'sum'
            }).reset_index()

            dispute_status_fig = px.bar(dispute_status, x='Carrier Name', y='Disputed Amount (USD)', color='Settlement Status',
                                        title="Settled vs Unsettled Disputes by Carrier")
            st.plotly_chart(dispute_status_fig)
        else:
            st.write("No data to display for the selected filter.")

    # Tab 4: Settlement Summary (Scenario)
    with tab4:
        st.subheader("Settlement Summary")
        
        # Scenario 1: Settlement Status by Carrier
        st.write("### Settlement Status by Carrier")
        if not filtered_df.empty:
            settlement_status = filtered_df.groupby(['Carrier Name', 'Settlement Status']).size().reset_index(name='Count')

            settlement_pie = px.pie(settlement_status, names='Settlement Status', values='Count', 
                                    title="Settlement Status by Carrier")
            st.plotly_chart(settlement_pie)
        else:
            st.write("No data to display for the selected filter.")

        # Scenario 2: Outstanding vs Settled Amounts
        st.write("### Outstanding vs Settled Amounts by Carrier")
        if not filtered_df.empty:
            outstanding_settlements = filtered_df[filtered_df['Settlement Status'] == 'Unsettled']
            settled_vs_outstanding = filtered_df.groupby(['Carrier Name', 'Settlement Status']).agg({
                'Invoice Amount (USD)': 'sum'
            }).reset_index()

            outstanding_vs_settled_fig = px.bar(settled_vs_outstanding, x='Carrier Name', y='Invoice Amount (USD)', color='Settlement Status',
                                                title="Outstanding vs Settled Amounts")
            st.plotly_chart(outstanding_vs_settled_fig)
        else:
            st.write("No data to display for the selected filter.")
