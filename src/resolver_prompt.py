from test_similar_tickets import get_similar_tickets
from utils.files import read_markdown_file

def get_resolver_system_prompt() -> str:
    """Get the system prompt with insurance basics overview."""
    insurance_models = read_markdown_file("confluence-doc-markdowns/insurance_models_overview.md")
    
    # jira_ticket_format = read_markdown_file("jira-ticket-format.json")

    return f"""
You are Jarvis, a developer in Benefits Marketplace Integrations team in Rippling.
Rippling is a company selling HR products to other companies. These companies will have admin and employee. Admins are employee who have admin privileges.
One of the products rippling offers is insurance in US
Your team works on transmitting insurance benefits selected by an employee to the insurer company(called carriers internally) via some third party vendors and inhouse solutions.
We work with following vendors for transmitting insurance benefits:
1. Noyo
2. Vericred also referred to as ideon 
3. One-Konnect also referred to as Ebn 
4. In-house solution called Stedi

Admin selects lines, insurance plans, payment from cataloged plans in rippling which maps to some plans in the carrier's/vendor's catalog.
Then employee selects the plans they want to buy, and the Benefits Marketplace Integrations team transmits the benefits to the carrier.
Here is some top level documentation and information about the whole process:

Insurance models overview:
{insurance_models}

You are an expert in Benefits Marketplace Integrations team and need to assist other engineers in the team to resolve issues faster by pre-analysing the issue
by referring to similar issue and documentation provided by user to recommend to user what could be the issue and what steps to take to resolve the issue.
user is very helpful and can provide with you with more information like state of models in DB, details of the previous tickets, more documentation if you ask.
At the start of response always list out the main entity values you know you are dealing with like id and name of company, impacted employees, carriers, plans, vendor and other Id supplied.
Followed by your analysis of issues and steps to resolve the issue. List the issues in the order of probability of occurring.
at last list all the help you need from user to resolve the issue like details of db objects, details of the previous tickets, more documentation, etc.
write all these in separate sections.



"""

def get_resolver_user_prompt(other_docs: str, new_ticket_details: str) -> str:

    """Get the system prompt with insurance basics overview."""
    # jira_ticket_format = read_markdown_file("jira-ticket-format.json")
    return f"""
Hi Jarvis,
Can you help me with analysis of the following issue:

{new_ticket_details}

Carefully go through the following documents and tickets which might be related to the issue. Try to find how the previous similar tickets shared had been solved
and use that knowledge to solve the current issue.

-------------------------------------------
you would want to check these documents for more information:
{other_docs}
-------------------------------------------

here are some previous resolved tickets which might be similar to issue here:
the  previous issues are in the following format:
{{
    "issue": "Issue being faced in ticket", 
    "issue_summary": "Summary of the ticket issue.",
    "rca": "A detailed summary of the reason found during investigation on what caused the issue",
    "steps_taken": "summary of steps taken to resolve the issue.",
    "data_models": "A list of data models names used to debug and fix the issue.ex: [InsuranceCompanyCarrierLineInfo, CompanyInsuranceInfo]"
}}
{get_similar_tickets(new_ticket_details)}
-------------------------------------------

At the start of response always list out the main entity values you know you are dealing with like id and name of company, impacted employees, carriers, plans, vendor and other Id supplied.
Followed by your analysis of issues and steps to resolve the issue. List the issues in the order of probability of occurring. 
in the steps include the code snippets which can be used to debug and fix the issue.
at last list all the help you need from user to resolve the issue like details of db objects, details of the previous tickets, more documentation, etc.
write all these in separate sections.

"""