FOLLOW_UP_PROMPT = """
Based on the conversation and messages above, give me a list of exact data model names that are relevant to the issue.
Output the response in the following JSON format, but do not render it as markdown:

{
    "company_id": "company_id",
    "company_plan_info_id": "company_plan_info_id" (if provided),
    "data_models": ["data_model_1", "data_model_2", "data_model_3"]
}
"""
