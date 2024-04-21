# mlx-lm macos + marimo + llama3 research assistant
## Entire concept and code and functions / SERP functions heavily copied from Matt Shumer @ https://github.com/mshumer/ai-researcher/blob/main/Claude_Researcher.ipynb (love your work, Matt!)
## My sole contribution on top of Matt's awesome notebook is putting it in Marimo and refactoring it to run on mlx-lm (parallel generate_text calls caused lots of crashes since it's running locally)
## Modify as you see fit!

import marimo

__generated_with = "0.4.2"
app = marimo.App()


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """#mlx-lm macos + marimo + llama3 research assistant
    ## Entire concept and code and functions / SERP functions heavily copied from Matt Shumer @ https://github.com/mshumer/ai-researcher/blob/main/Claude_Researcher.ipynb (love your work, Matt!)
    ## My sole contribution on top of Matt's awesome notebook is putting it in Marimo and refactoring it to run on mlx-lm (parallel generate_text calls caused lots of crashes since it's running locally)
    ## Modify as you see fit!
    ### Usage: Ensure you set SERP_API_KEY """
    )
    return


@app.cell
def __():
    import requests
    import json
    import re
    from mlx_lm import load, generate
    import mlx.core as mx

    DEFAULT_TEMP = 0.6
    DEFAULT_TOP_P = 1.0
    SERP_API_KEY = ""

    model = "/Storage/Meta-Llama-3-8B-Instruct-8bit-mlx"
    max_tokens = 4096
    mx.random.seed(0)
    tokenizer_config = {"trust_remote_code": False}
    model, tokenizer = load(model, adapter_path=None, tokenizer_config=tokenizer_config)
    tokenizer.chat_template = tokenizer.default_chat_template

    def remove_first_line(test_string):
        if test_string.startswith("Here") and test_string.split("\n")[
            0
        ].strip().endswith(":"):
            return re.sub(r"^.*\n", "", test_string, count=1)
        return test_string

    def generate_text(prompt, max_tokens=8192):
        messages = [
            {
                "role": "system",
                "content": "You are a world-class researcher. Analyze the given information and generate a well-structured report.",
            },
            {"role": "user", "content": prompt},
        ]

        formatted_prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        response = generate(
            model,
            tokenizer,
            formatted_prompt,
            DEFAULT_TEMP,
            max_tokens,
            True,
            top_p=DEFAULT_TOP_P,
        )
        response = re.sub(r'\\(["\n])', r"\1", response)
        return response

    return (
        DEFAULT_TEMP,
        DEFAULT_TOP_P,
        SERP_API_KEY,
        generate,
        generate_text,
        json,
        load,
        max_tokens,
        model,
        mx,
        re,
        remove_first_line,
        requests,
        tokenizer,
        tokenizer_config,
    )


@app.cell
def __(mo):
    # User input
    research_topic = mo.ui.text(
        label="Enter research topic",
        value="best practices for building a marimo app using mlx-lm and llama3",
    )
    return (research_topic,)


@app.cell
async def __(
    SERP_API_KEY,
    e,
    generate_text,
    json,
    mo,
    requests,
    research_topic,
):
    def search_web(search_term):
        url = f"https://serpapi.com/search.json?q={search_term}&api_key={SERP_API_KEY}"
        response = requests.get(url)
        data = response.json()
        print(json.dumps(data, indent=2))  # Pretty print the JSON data
        return data

    async def generate_subtopic_report(subtopic):
        search_data = []
        all_queries = []

        print(f"Generating initial search queries for subtopic: {subtopic}...")
        with mo.status.spinner(
            title=f"Generating initial search queries for subtopic: {subtopic}..."
        ):
            initial_queries_prompt = f"Generate 3 search queries to gather information on the subtopic '{subtopic}'. Return your queries in a Python-parseable list. Return nothing but the list. Do so in one line. Start your response with [\""
            initial_queries = json.loads(
                generate_text_with_retry(initial_queries_prompt)
            )

        print(initial_queries)
        all_queries.extend(initial_queries)

        for i in range(3):
            print(f"Performing search round {i+1} for subtopic: {subtopic}...")
            with mo.status.spinner(
                title=f"Performing search round {i+1} for subtopic: {subtopic}..."
            ):
                for query in initial_queries:
                    search_results = search_web(query)
                    search_data.append(search_results)

            print(f"Generating additional search queries for subtopic: {subtopic}...")
            with mo.status.spinner(
                title=f"Generating additional search queries for subtopic: {subtopic}..."
            ):
                additional_queries_prompt = f"Here are the search results so far for the subtopic '{subtopic}':\n\n{str(search_data)}\n\n---\n\nHere are all the search queries you have used so far for this subtopic:\n\n{str(all_queries)}\n\n---\n\nBased on the search results and previous queries, generate 3 new and unique search queries to expand the knowledge on the subtopic '{subtopic}'. Return your queries in a Python-parseable list. Return nothing but the list. Do so in one line. Start your response with [\""
                additional_queries = json.loads(
                    generate_text_with_retry(additional_queries_prompt)
                )

            initial_queries = additional_queries
            all_queries.extend(additional_queries)

        print(f"Generating initial report for subtopic: {subtopic}...")
        with mo.status.spinner(
            title=f"Generating initial report for subtopic: {subtopic}..."
        ):
            report_prompt = f"When writing your report, make it incredibly detailed, thorough, specific, and well-structured. Use Markdown for formatting. Analyze the following search data and generate a comprehensive report on the subtopic '{subtopic}':\n\n{str(search_data)}"
            report = generate_text_with_retry(report_prompt)

        for i in range(3):
            print(
                f"Analyzing report and generating additional searches (Round {i+1}) for subtopic: {subtopic}..."
            )
            with mo.status.spinner(
                title=f"Analyzing report and generating additional searches (Round {i+1}) for subtopic: {subtopic}..."
            ):
                analysis_prompt = f"Analyze the following report on the subtopic '{subtopic}' and identify areas that need more detail or further information:\n\n{report}\n\n---\n\nHere are all the search queries you have used so far for this subtopic:\n\n{str(all_queries)}\n\n---\n\nGenerate 3 new and unique search queries to fill in the gaps and provide more detail on the identified areas. Return your queries in a Python-parseable list. Return nothing but the list. Do so in one line. Start your response with [\""
                additional_queries = json.loads(
                    generate_text_with_retry(analysis_prompt)
                )

            all_queries.extend(additional_queries)

            round_search_data = []
            for query in additional_queries:
                search_results = search_web(query)
                round_search_data.append(search_results)

            print(
                f"Updating report with additional information (Round {i+1}) for subtopic: {subtopic}..."
            )
            with mo.status.spinner(
                title=f"Updating report with additional information (Round {i+1}) for subtopic: {subtopic}..."
            ):
                update_prompt = f"Update the following report on the subtopic '{subtopic}' by incorporating the new information from the additional searches. Keep all existing information... only add new information:\n\n{report}\n\n---\n\nAdditional search data for this round:\n\n{str(round_search_data)}\n\n---\n\nGenerate an updated report that includes the new information and provides more detail in the identified areas. Use Markdown for formatting."
                report = generate_text_with_retry(update_prompt)

        print(f"Generating boss feedback for subtopic: {subtopic}...")
        with mo.status.spinner(
            title=f"Generating boss feedback for subtopic: {subtopic}..."
        ):
            feedback_prompt = f"Imagine you are the boss reviewing the following report on the subtopic '{subtopic}':\n\n{report}\n\n---\n\nProvide constructive feedback on what information is missing or needs further elaboration in the report. Be specific and detailed in your feedback."
            feedback = generate_text_with_retry(feedback_prompt, max_tokens=1000)

        print(
            f"Generating final round of searches based on feedback for subtopic: {subtopic}..."
        )
        with mo.status.spinner(
            title=f"Generating final round of searches based on feedback for subtopic: {subtopic}..."
        ):
            final_queries_prompt = f"Based on the following feedback from the boss regarding the subtopic '{subtopic}':\n\n{feedback}\n\n---\n\nGenerate 3 search queries to find the missing information and address the areas that need further elaboration. Return your queries in a Python-parseable list. Return nothing but the list. Do so in one line. Start your response with [\""
            final_queries = json.loads(generate_text_with_retry(final_queries_prompt))

        all_queries.extend(final_queries)

        final_search_data = []
        for query in final_queries:
            search_results = search_web(query)
            final_search_data.append(search_results)

        print(f"Updating report with final information for subtopic: {subtopic}...")
        with mo.status.spinner(
            title=f"Updating report with final information for subtopic: {subtopic}..."
        ):
            final_update_prompt = f"Update the following report on the subtopic '{subtopic}' by incorporating the new information from the final round of searches based on the boss's feedback:\n\n{report}\n\n---\n\nFinal search data:\n\n{str(final_search_data)}\n\n---\n\nGenerate the final report that addresses the boss's feedback and includes the missing information. Use Markdown for formatting."
            final_report = generate_text_with_retry(final_update_prompt)

        print(f"Final report generated for subtopic: {subtopic}!")
        return final_report

    def generate_comprehensive_report(topic, subtopic_reports):
        print("Generating comprehensive report...")
        with mo.status.spinner(title="Generating comprehensive report..."):
            comprehensive_report_prompt = f"Generate a comprehensive report on the topic '{topic}' by combining the following reports on various subtopics:\n\n{subtopic_reports}\n\n---\n\nEnsure that the final report is well-structured, coherent, and covers all the important aspects of the topic. Make sure that it includes EVERYTHING in each of the reports, in a better structured, more info-heavy manner. Nothing -- absolutely nothing, should be left out. If you forget to include ANYTHING from any of the previous reports, you will face the consequences. Include a table of contents. Leave nothing out. Use Markdown for formatting."
            comprehensive_report = generate_text(
                comprehensive_report_prompt, max_tokens=4000
            )

        print("Comprehensive report generated!")
        return comprehensive_report

    def generate_text_with_retry(prompt, max_tokens=4000, num_retries=3):
        for attempt in range(num_retries):
            try:
                return generate_text(prompt, max_tokens)
            except Exception as e:
                print(
                    f"Error generating text (attempt {attempt+1}/{num_retries}): {str(e)}"
                )
                if attempt < num_retries - 1:
                    print("Retrying...")
                else:
                    raise e

    # Generate subtopic checklist
    with mo.status.spinner(title="Generating subtopic checklist..."):
        subtopic_checklist_prompt = f"Generate a detailed checklist of subtopics to research for the topic '{research_topic.value}'. Return your checklist in a Python-parseable list. Return nothing but the list. Do so in one line. Maximum five sub-topics. Start your response with [\""
        subtopic_checklist = json.loads(
            generate_text_with_retry(subtopic_checklist_prompt)
        )

    print(f"Subtopic Checklist: {subtopic_checklist}")

    subtopic_reports = mo.ui.tabs(
        {
            "Tab 1": mo.md("# Content for Tab 1"),
            "Tab 2": mo.md("# Content for Tab 2"),
        }
    )

    for subtopic in subtopic_checklist:
        report = await generate_subtopic_report(subtopic)
        subtopic_reports.append({"title": subtopic, "content": mo.md(report)})

    # Combine subtopic reports into a comprehensive report
    with mo.status.spinner(title="Generating comprehensive report..."):
        comprehensive_report = mo.ui.accordion(
            mo.ui.accordion_item(
                title="Comprehensive Report",
                content=mo.ui.markdown(
                    generate_comprehensive_report(
                        research_topic.value,
                        "\n\n".join(
                            [report for _, report in subtopic_reports.value.items()]
                        ),
                    )
                ),
            )
        )

    generate_button = mo.ui.button(label="Generate Reports")
    generate_button.on_click(lambda: None)  # Trigger report generation

    mo.vstack(
        [research_topic, generate_button, subtopic_reports, comprehensive_report],
        align="stretch",
        gap=1,
    )
    return (
        comprehensive_report,
        generate_button,
        generate_comprehensive_report,
        generate_subtopic_report,
        generate_text_with_retry,
        report,
        search_web,
        subtopic,
        subtopic_checklist,
        subtopic_checklist_prompt,
        subtopic_reports,
    )


if __name__ == "__main__":
    app.run()
