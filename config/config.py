from collections import namedtuple



account_defaults = {
    'ACL': {'xbrl':'FinancingReceivableAllowanceForCreditLosses','term':'Allowance for credit loss'},
    'ALLL': {'xbrl':'FinancingReceivableAllowanceForCreditLosses','term':'allowance for loan and lease losses'},
    'PCL': {'xbrl':'ProvisionForLoanLeaseAndOtherLosses','term':'Provision for credit loss'},
    'ChargeOffs': {'xbrl':'FinancingReceivableAllowanceForCreditLossesWriteOffsNet','term':'charge-off'},
    'NetChargeOffs': {'xbrl':'FinancingReceivableAllowanceForCreditLossesWriteOffsNet','term':'charge-off'},
    'Loans': {'xbrl':'NotesReceivableGross','term':'Loan'},
    'ACLpctLoan': {'xbrl':'FinancingReceivableAllowanceForCreditLossToOutstandingPercent','term':'as percent of loans'},
    'ALLLpctLoan': {'xbrl':'FinancingReceivableAllowanceForCreditLossToOutstandingPercent','term':'as percent of loans'},
    'ALLLpctLHFI': {'xbrl':'FinancingReceivableAllowanceForCreditLossToOutstandingPercent','term':'as percent of LHFI'}
}

AccountRecord = namedtuple(
    "AccountRecord",
    [   'name',
        'xbrl',
        'table_name',
        'table_account',
        'table_column',
        'scale',
        'discover_terms',
        'search_terms',
        'exhibits'
    ]
)

FirmRecord = namedtuple(
    "FirmRecord",
    [   'Firm',
        'accounts'
    ]
)





firms_8k = [
    {
    'cik': 72971,
    'ticker': 'WFC',
    'accounts': {
        'ACL': {
            'table': 'ALLOCATION OF ALLOWANCE FOR CREDIT LOSSES FOR LOANS',
            'term': 'Total allowance for credit losses for loans'
        },
        'PCL': {
            'table': 'CONSOLIDATED STATEMENT OF INCOME',
            'term': 'Provision for credit losses'
        },
        'ChargeOff': {
            'table': 'CHANGES IN ALLOWANCE FOR CREDIT LOSSES FOR LOANS',
            'term': 'Net loan charge-offs'
        },
        'Loans': {
            'table': 'SUMMARY FINANCIAL DATA',
            'term': 'Loans'
        },
        'ACLpctLoan':{
            'table': 'CHANGES IN ALLOWANCE FOR CREDIT LOSSES FOR LOANS',
            'term': 'Allowance for credit losses for loans as a percentage of Total loans'
        }
        }
    },
    {'cik': 36104,
    'ticker': 'USB',
    'exhibit': 'EX-99.1',
    'accounts': {
        'ACL': {
            'table': 'ALLOWANCE FOR CREDIT LOSSES',
            'term': 'Total\tallowance\tfor\tcredit\tlosses'
        }
    }
    },
    {'cik': 713676,
    'ticker': 'PNC',
    'exhibit': 'EX-99.1',
    'accounts': {
        'ACL': {
            'table': 'ALLOWANCE FOR CREDIT LOSSES',
            'term': 'Allowance for credit losses'
        }
    }
    },
]
