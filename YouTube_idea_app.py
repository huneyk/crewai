import os
from dotenv import load_dotenv
import streamlit as st
from crewai import Agent, Task, Crew
from crewai.process import Process
from crewai_tools import SerperDevTool, WebsiteSearchTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

serper_api_key = os.getenv("SERPER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize tools and LLM
llm = ChatOpenAI(model="gpt-4o")
search_tool = SerperDevTool()
web_rag_tool = WebsiteSearchTool()
scrap_tool = ScrapeWebsiteTool()

# Streamlit UI
st.title("YouTube Content Research and Planning")
st.write("Generate YouTube content ideas and plans tailored to your preferences.")

# Input fields

tone_options = ["funny", "informative", "emotional"]
language_options = ["English", "Korean", "Japanese"]
format_options = ["YouTube Video", "YouTube Reels", "TicToc", "Facebook Reels"]

field = st.text_input("Enter the main field of expertise:")
topic = st.text_input("Please specify topics of the field:")
select_tone = st.selectbox("Select the tone you want:", tone_options)
select_format = st.selectbox("Select the format you want:", format_options)
select_lang = st.selectbox("Select the language you want:", language_options)
file_name = st.text_input("Enter the file name for the result:")

if st.button("Generate Content Plan"):
    if not field or not topic or not file_name:
        st.error("Please fill in all the required fields.")
    else:
        # Define agents
        researcher = Agent(
            role=f"Professional Researcher about {field}",
            goal=f"""
            The Agent acts as a professional researcher specialized in generating high-quality {select_format} content ideas. 
            Its primary responsibility is to search the web for information, insights, and resources relevant to {field}.
            Additionally, the Agent tailors its findings to align with {select_tone} to ensure the final product resonates 
            with the target audience.
            """,
            backstory=f"""
            This Agent is a product of innovative push to empower creators in the competitive landscape 
            of digital media. Inspired by the challenges content creators face in balancing creative ideation 
            with time-consuming research, the Agent was trained with an extensive database of multimedia trends, 
            audience preferences, and creative storytelling techniques.
            """,
            tools=[search_tool, web_rag_tool],
            verbose=True,
            max_iter=10,
            llm=llm,
        )

        creator = Agent(
            role="Professional " + select_format + "Creator",
            goal=f"""
            The Agent’s mission is to conceptualize and craft engaging {select_format} content tailored to the topic of {field} and {topic} in the tone of {select_tone}.
            The Agent should write the result in {select_lang}.
            """,
            backstory=f"""
            Born out of a commitment to revolutionizing the content creation process, this Agent is the result 
            of years of collaborative development with digital marketing experts, storytelling professionals, 
            and platform-specific growth strategists.
            """,
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )

        interpreter = Agent (
            role = "Professional and creative interpreter of many languages",
            goal = "Interprete the results from English to "+ select_lang + "in very natural and friendly tone. The result is very easy to read and natural like a native speaker.",
            backstory = "All the result should be interpreted. The tone of the text is professional and intuitive.",
            verbose = True,
            llm = llm
        )
        
        writer = Agent (
            role = f"Very gifted writer of {select_format} script",
            goal = f"Organize a detailed {select_format} video storyboard and script based on the structure presented by the interpreter.",
            backstory = "Write in very engaging and friendly manner.",
            Verbose = True,
            llm = llm
        )
        
# Define tasks
        research = Task(
            description=f"""
            This agent's task is to perform comprehensive web searches and gather relevant, high-quality 
            resources aligned with the topic of {field} and {topic} in the tone of {select_tone}.
            """,
            expected_output="""
            - A list of key resources (articles, videos, studies, or trends).  
            - Highlighted insights that align with the specified tone.  
            - An overview of potential angles for storytelling or content structuring.  
            """,
            agent=researcher,
        )

        create = Task(
            description=f"""
            This agent's task is to design an engaging and structured {select_format} content plan tailored to the topic 
            of {field} and {topic} in the tone of {select_tone} in {select_lang}.
            """,
            expected_output=f"""
            5 sets of the following result:
            - A video title that is optimized for both {select_tone} and discoverability.
            - A step-by-step storyboard that includes timing, visuals, key messages and narratives for each segment in detail.
            - Suggested CTAs with placement and wording that encourage audience interaction.
            - A summary of how the content aligns with the chosen tone and audience expectations.
            """,
            agent=creator,
        )

        interprete = Task (
            description = "Interprete the result into " + select_lang +".",
            expected_output = "5 sets of interpreted results",
            agent = interpreter,
            output_file=f"idea_{file_name}_{select_format}_{field}.md"
              
        )
       
        ### write = Task (
        #    description = "write engaging storyboard and scripts in detail for YouTube video",
        #    expected_output = "5 sets of Detailed storyboard and scripts in dialogue style. Each script consists of a few lines of friendly dialogue.",
        #    agent = writer,
            
        #    "  
        #)
        ###
        

        # Run crew
        crew = Crew(
            agents=[researcher, creator, interpreter],
            tasks=[research, create, interprete],
            verbose=True,
            process=Process.sequential,
        )

        result = crew.kickoff()
        st.success("Content plan generated successfully!")
        st.write ("Result saved to file:", f"idea_{file_name}_{select_format}_{field}.md")
