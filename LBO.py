from operator import lt
import streamlit as st
import pandas as pd
import numpy as np
from Functions import *
import plotly.express as px
import itertools





st.title('Business Acquisition Example LBO')

inputs, debt_inputs, outcomes = st.columns([1,1,2])


with inputs:
    st.header("Purchase Price")
    ltm_ebitda = st.number_input("LTM EBITDA", step= 1)
    entry_multiple = st.number_input("Entry Multiple X", step= 1)
    equity_pct =  st.number_input("Equity percentage (%)", step= 1)


# create the initial values 
inputs = initial_values(ltm_ebitda,entry_multiple,equity_pct)

purchase_price = inputs["purchase_price"]
equity = inputs["equity"]
debt = inputs["debt"]
equity_percentage = inputs["equity_percentage"]
debt_percentage = inputs["debt_percentage"]


with debt_inputs:
    st.header("Debt Service")
    interest_rate = st.number_input("Interest rate %", step= 1)
    term = st.number_input("Term (years)", step= 1)
    growth = st.number_input("YOY Growth (%)", step= 1)
      
 

outcomes.header("Capital Structure")   
with outcomes:
    outcomes.metric(label = "Equity",
    value = f"${equity :,.0f}",delta = f"{equity_percentage:.0%}")
    outcomes.metric(label = "Debt",
    value = f"${debt :,.0f}", delta = f"{debt_percentage:.0%}")
    outcomes.metric(label = "Enterprise Value", 
    value = f"${purchase_price :,.0f}")

# Amortization Table

Ebidta_tab, debt_balance = st.tabs(["EDBITA", "Loan Amortization",])

df = amortization_table(debt,interest_rate,term)

with Ebidta_tab:
    columns_name = ['names','year1', 'year2', 'year3', 'year4', 'year5']
    columns_name = st.columns([1]*(len(columns_name)))
    names_list = ["EBITDA","Interest","______","Net Income",]
    
# Add the name of the concepts to the left
    with columns_name[0]:
        st.subheader("Concept")
        for i in names_list:
            st.write(i)
# Create a colum with the value of EDBITA, Interest and Net Income 
    for i,j in enumerate(columns_name[1:], start=1):
        with j:
            projections(i,growth,ltm_ebitda,df) 

    # create loan Amortization

    st.subheader("Capital Structure")

    try:
        df_capital = capital_structure(df,purchase_price)
        capital_graph = px.bar(
        df_capital, 
        x= df_capital.index,    
        y = ['Debt','Equity'],
        barmode = 'stack',
        title="", 
        text_auto='.3s'
         )

        st.write("The numbers are the end  balance capital structure")
     
        capital_graph.update_layout(
        xaxis_title="Year",
        yaxis_title=""
        )

        st.plotly_chart(capital_graph, theme="streamlit",
         use_container_width=True)
    except:
        pass

        
with debt_balance:   
    st.header("Amortization Table")
    table = format_currency(df,list(df.columns.tolist()))
    st.write(table)
    try:
        fig = px.bar(
            df, 
            x= df.index,    
            y = ['Principal','Interest'],
            barmode = 'stack',
            title="Payment Distribution", 

            text_auto='.3s'
            )
        
        fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Payment"
        )

        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    except:
        pass


# Exit and sensitive analysis      
st.subheader('Exist')
exit_enterprise_value, exit_moic, exit_irr  = st.columns([1,1,1])

exit_KPI = exit_indicators(df,growth,ltm_ebitda,
                entry_multiple,equity)

exit_enterprise_value.metric(label = "Enterprise Value",
        value = f"{exit_KPI['e_ev']:,.0f}")                                                                     

exit_moic.metric(label = "MOIC",
        value = f"{exit_KPI['moic'] :,.2f}x")

exit_irr.metric(label = "IRR",
        value = f"{exit_KPI['irr_exit'] :,.2%}")

st.subheader('Sensitivity Analysis')
loan_sen, growth_sen, equity_sen = st.tabs(["Loan", "Growth", "Equity",])

with loan_sen:
    
    term_sensitive = st.slider('Select a new term for the loan', 1, 20, term)
    interest_df = amortization_table(debt,interest_rate,term_sensitive)
    exit_KPI_sen = exit_indicators(interest_df,growth,ltm_ebitda,
                entry_multiple,equity)

    exit_enterprise_value_s_l, exit_moic_s_l, exit_irr_s_l  = st.columns([1,1,1])
    
    exit_enterprise_value_s_l.metric(label = "Enterprise Value",
        value = f"{exit_KPI_sen['e_ev']:,.0f}", 
        delta=f"{(exit_KPI_sen['e_ev']-exit_KPI['e_ev']):,.0f}")                                                                     

    exit_moic_s_l.metric(label = "MOIC",
        value = f"{exit_KPI_sen['moic'] :,.2f}x", 
        delta=f"{(exit_KPI_sen['moic']-exit_KPI['moic']):,.2f}")  
                                                                            

    exit_irr_s_l.metric(label = "IRR",
        value = f"{exit_KPI_sen['irr_exit'] :,.2%}",
        delta= f"{(exit_KPI_sen['irr_exit']-exit_KPI['irr_exit'])*100 :,.0f} basis points") 

with growth_sen:
    
    growth_sen_value = st.slider('Select a new growth rate', 0, 100, growth)
    exit_KPI_sen_g = exit_indicators(df,growth_sen_value,ltm_ebitda,
                entry_multiple,equity)

    exit_enterprise_value_s_g, exit_moic_s_g, exit_irr_s_g  = st.columns([1,1,1])
    
    exit_enterprise_value_s_g.metric(label = "Enterprise Value",
        value = f"{exit_KPI_sen_g['e_ev']:,.0f}", 
        delta=f"{(exit_KPI_sen_g['e_ev']-exit_KPI['e_ev']):,.0f}")                                                                     

    exit_moic_s_g.metric(label = "MOIC",
        value = f"{exit_KPI_sen_g['moic'] :,.2f}x", 
        delta=f"{(exit_KPI_sen_g['moic']-exit_KPI['moic']):,.2f}")  
                                                                            

    exit_irr_s_g.metric(label = "IRR",
        value = f"{exit_KPI_sen_g['irr_exit'] :,.2%}",
        delta= f"{(exit_KPI_sen_g['irr_exit']-exit_KPI['irr_exit'])*100 :,.0f} basis points") 

with equity_sen:
    
    
    equity_pct_sen = st.slider('Select new % of equity', 0, 100, equity_pct)
    equity_sen_value = initial_values(ltm_ebitda,entry_multiple,equity_pct_sen)["equity"]
    exit_KPI_sen_e = exit_indicators(df,growth,ltm_ebitda,
                entry_multiple,equity_sen_value)

    exit_enterprise_value_s_e, exit_moic_s_e, exit_irr_s_e  = st.columns([1,1,1])
    
    exit_enterprise_value_s_e.metric(label = "Enterprise Value",
        value = f"{exit_KPI_sen_e['e_ev']:,.0f}", 
        delta=f"{(exit_KPI_sen_e['e_ev']-exit_KPI['e_ev']):,.0f}")                                                                     

    exit_moic_s_e.metric(label = "MOIC",
        value = f"{exit_KPI_sen_e['moic'] :,.2f}x", 
        delta=f"{(exit_KPI_sen_e['moic']-exit_KPI['moic']):,.2f}")  
                                                                            

    exit_irr_s_e.metric(label = "IRR",
        value = f"{exit_KPI_sen_e['irr_exit'] :,.2%}",
        delta= f"{(exit_KPI_sen_e['irr_exit']-exit_KPI['irr_exit'])*100 :,.0f} basis points")

        