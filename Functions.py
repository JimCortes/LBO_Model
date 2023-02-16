import streamlit as st
#import numpy_financial as npf
import pandas as pd
import numpy as np
import pickle
import itertools

def irr(moic,year):
    return moic **(1/year) -1

def appreciation(interest_rate,year):
    return (1+interest_rate)**year 


def projections(year:int,growth:int,ltm_ebitda, df):
    try:
        st.subheader(f"Year {year}")
        interest = df.loc[year,'Interest'] if year in df.index else 0
        ebitda = appreciation(growth/100,year) * ltm_ebitda
        net_income = ebitda - interest
        st.write(f'${ebitda:,.0f}')
        st.write(f'${interest:,.0f}')
        st.markdown("---")
        st.write(f'${net_income:,.0f}')
     
    except:
        interest = 0
        ebitda = 0
        net_income = 0 
        st.write(f'${ebitda:,.0f}')
        st.write(f'${interest:,.0f}')
        st.markdown("---")
        st.write(f'${net_income:,.0f}')


def capital_structure(df,EV):
    df = df.head(5)
    
    df["Debt"] = df["Balance"] 
    df["Equity"] = EV - df["Debt"]
    df = df[["Equity","Debt"]]

    if df.shape[0] < 5:
        new_data = {'Year': range(df.shape[0]+1, 6), 
        'Balance': [0]*(5-df.shape[0]), 'equity':[0]*(5-df.shape[0])}
        df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
        df["Equity"] = EV - df["Debt"].map(lambda x: x if x>0 else 0)

        df.index += 1
    
    return df 

  
def exit_indicators(df,growth, ltm_ebitda, entry_multiple, equity):
    try:
        e_ev =  appreciation(growth/100,5) * ltm_ebitda * entry_multiple
        debt_balance = df.loc[5,'Balance'] if df.shape[0] >= 5 else 0
        moic =  (e_ev - debt_balance ) / equity
        irr_exit =  irr(moic,5)
    except:
        e_ev = 0
        moic = 0
        irr_exit = 0 

    return {"e_ev":e_ev, 
            "moic":moic,
            "irr_exit":irr_exit }

def amortization_table(principal, interest_rate, term):
    
    try:
        interest_rate = (interest_rate / 100) / 12  
        payment = (principal * interest_rate) / (1 - (1 + interest_rate) ** (-term))
        table = []
        balance = principal
        for i in range(term):
            interest = balance * interest_rate
            principal_paid = payment - interest
            balance -= principal_paid
            table.append({'Payment': payment,'Principal': principal_paid, 
                'Interest': interest,'Balance': balance})
        df = pd.DataFrame(table)
        df.index += 1
    except:
        df = pd.DataFrame()
    
    return  df
 
def format_currency(df, columns):
    df = df.copy()
    for column in columns:
        df[column] = df[column].map(lambda x: f"${x:,.0f}")
    return df

def initial_values(ltm_ebitda,entry_multiple,equity_pct):
    try:
        purchase_price = ltm_ebitda * entry_multiple
        equity = purchase_price * (equity_pct/100)
        debt = purchase_price - equity
        equity_percentage = equity/purchase_price
        debt_percentage = debt/purchase_price
    except:
        purchase_price = 0
        equity = 0
        debt  = 0
        equity_percentage = 0 
        debt_percentage = 0  
    return {"purchase_price":purchase_price, "equity":equity,
                "debt":debt, "equity_percentage":equity_percentage,
                "debt_percentage":debt_percentage
                 }

