import streamlit as st
from streamlit_option_menu import option_menu
import PyPDF2
import docx
import networkx as nx
import matplotlib.pyplot as plt

# Sample company internship openings
companies = [
    {"name": "Google", "role": "Software Engineering Intern", "skills": ["Python", "Machine Learning", "Data Structures"]},
    {"name": "Microsoft", "role": "Cloud Computing Intern", "skills": ["Azure", "Networking", "Cybersecurity"]},
    {"name": "Amazon", "role": "Data Science Intern", "skills": ["SQL", "Pandas", "AI/ML"]},
    {"name": "Tesla", "role": "Embedded Systems Intern", "skills": ["C", "C++", "Microcontrollers"]},
    {"name": "Meta", "role": "Frontend Development Intern", "skills": ["React", "JavaScript", "UI/UX Design"]},
    {"name": "IBM", "role": "AI Research Intern", "skills": ["Deep Learning", "Python", "c"]},
    {"name": "Apple", "role": "iOS Development Intern", "skills": ["Swift", "Objective-C", "Mobile Development"]},
    {"name": "Netflix", "role": "Backend Developer Intern", "skills": ["Django", "Flask", "API Development"]},
    {"name": "SpaceX", "role": "Aerospace Engineering Intern", "skills": ["MATLAB", "C++", "Control Systems"]},
    {"name": "Intel", "role": "Chip Design Intern", "skills": ["VHDL", "Verilog", "Hardware Design"]}
]

# Sample student applicants
students = {
    "Alice": ["Python", "Machine Learning", "SQL"],
    "Bob": ["Java", "Spring Boot", "Microservices"],
    "Charlie": ["C++", "Data Structures", "Algorithms"],
    "David": ["Python", "Django", "JavaScript"],
    "Emma": ["React", "Node.js", "MongoDB"],
    "Frank": ["Data Science", "R", "Python"],
    "Grace": ["Cloud Computing", "AWS", "DevOps"],
    "Hannah": ["Cybersecurity", "Penetration Testing", "Networking"],
    "Ian": ["Game Development", "Unity", "C#"],
    "Julia": ["AI", "Deep Learning", "TensorFlow"]
}

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()]) # Loops pages and combines their text

    return text if text else "No readable text found in the PDF."

# Extract text from DOCX
def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs]) # Extracts and joins all paragraph text from the .docx file


# Main App

def main():
    st.set_page_config(page_title=" ForsaFinder", page_icon="🔍", layout="wide")

    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Job Recommendation", "Interactive Matching"],
            icons=["house", "briefcase", "graph-up"],
            menu_icon="menu-hamburger",
            default_index=0
        )

    if selected == "Home":
        st.title("Welcome to  ForsaFinder 🔍")
        st.image("https://i.insider.com/63b471f9db9ee80019386a4b?width=800&format=jpeg&auto=webp", width=700)
        st.markdown("<span style='color:#2E8B57; font-weight:bold;'>Find your perfect internship based on your resume.</span>", unsafe_allow_html=True)

        st.subheader("📢 Companies Hiring Interns")
        for company in companies:
            st.markdown(f"**{company['name']}** - *{company['role']}*")
            st.markdown(f"<u>Required Skills:</u> {', '.join(company['skills'])}", unsafe_allow_html=True)

    elif selected == "Job Recommendation":
        job_recommendation_page()

    elif selected == "Interactive Matching":
        interactive_graph_page()

# Extracted from previous definition to avoid repetition

def job_recommendation_page():
    st.title("Job Recommendation")
    st.write("Upload your resume to find the best job matches using graph matching.")

    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

    if uploaded_file is not None:
        st.success("Resume uploaded successfully! Analyzing your skills...")

        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx(uploaded_file)
        else:
            resume_text = "Invalid file type."

        st.subheader("Extracted Resume Content")
        with st.expander("View Resume Text"):
            st.text_area("Resume Text", resume_text, height=250)

        resume_words = set(resume_text.lower().split())

        G = nx.Graph()
        student_node = "Student"
        G.add_node(student_node, bipartite=0)

        edge_labels = {}
        for company in companies:
            G.add_node(company["name"], bipartite=1)
            required_skills = set(skill.lower() for skill in company["skills"])
            matching_skills = resume_words & required_skills

            if matching_skills:
                score = len(matching_skills)
                G.add_edge(student_node, company["name"], weight=score)
                edge_labels[(student_node, company["name"])] = ", ".join(matching_skills)

        matching = nx.algorithms.matching.max_weight_matching(G, maxcardinality=True)

        st.subheader("🔗 Best Matching Internship")
        match_found = False
        for u, v in matching:
            if student_node in (u, v):
                company = v if u == student_node else u
                match_found = True
                role = next(c["role"] for c in companies if c["name"] == company)
                skills = edge_labels.get((student_node, company), edge_labels.get((company, student_node), ""))
                st.success(f"✅ **{role}** at **{company}**")
                st.write(f"📌 **Matching Skills:** {skills}")
        if not match_found:
            st.warning("No strong match found. Try improving your resume skills!")

        st.subheader("📊 Matching Graph")
        fig, ax = plt.subplots(figsize=(12, 7))
        pos = nx.bipartite_layout(G, nodes=[student_node])

        node_colors = ["lightgreen" if node == student_node else "lightblue" for node in G.nodes()]
        edge_colors = ["red" if (u, v) in matching or (v, u) in matching else "gray" for u, v in G.edges()]
        edge_widths = [2.5 if (u, v) in matching or (v, u) in matching else 1.0 for u, v in G.edges()]

        nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color=edge_colors,
                node_size=2000, font_size=10, ax=ax, width=edge_widths)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, ax=ax)

        st.pyplot(fig)

# ---------- Page 3: Interactive Matching Between Students and Companies ----------
def interactive_graph_page():
    st.title("🧠 Interactive Matching Graph")

    # Create bipartite graph
    B = nx.Graph()  #Initializes an empty undirected graph 
    edge_labels = {} #Initializes an empty dictionary to store edge labels

    B.add_nodes_from(students.keys(), bipartite=0) ## Adds student nodes to the left side of the bipartite graph
    B.add_nodes_from([c["name"] for c in companies], bipartite=1)

    #add edges between students and companies in the  graph based on skill matching
    for student, skills in students.items():
        for company in companies:
            required_skills = set(skill.lower() for skill in company["skills"]) # Converts company skills to lowercase set for matching
            matching = set(skill.lower() for skill in skills) & required_skills #intersection
            if matching:
                B.add_edge(student, company["name"], weight=len(matching))
                edge_labels[(student, company["name"])] = ", ".join(matching)

    # Compute maximum weight matching
    matching = nx.algorithms.matching.max_weight_matching(B, maxcardinality=True)

    # User selects a student or company
    entity_type = st.selectbox("Select entity type", ["Student", "Company"])
    if entity_type == "Student":
        selected = st.selectbox("Choose a student", list(students.keys()))
    else:
        selected = st.selectbox("Choose a company", [c["name"] for c in companies])

    # Find the match from the matching set
    match = None # Sets up match to store the selected node’s partner
    for u, v in matching:
        if selected in (u, v):
            match = v if u == selected else u #sets match to the other node in the pair
            break

    if match:
        st.success(f"🔗 Match Found: {selected} ↔ {match}")
        st.markdown(f"**Skills Matched:** {edge_labels.get((selected, match)) or edge_labels.get((match, selected))}")
    else:
        st.warning("No match found in the optimal assignment.")

    # Draw the graph
    st.subheader("📈 Matching Graph") #title
    pos = nx.bipartite_layout(B, students.keys())  # Clear left-right layout
    fig, ax = plt.subplots(figsize=(16, 9)) #large figure

    nx.draw_networkx_nodes(B, pos, nodelist=students.keys(), node_color="lightblue", node_size=2000, label="Students")
    nx.draw_networkx_nodes(B, pos, nodelist=[c["name"] for c in companies], node_color="lightgreen", node_size=2000, label="Companies")
    edge_colors = ["red" if (u, v) in matching or (v, u) in matching else "gray" for u, v in B.edges()] #red if they best match
    edge_widths = [2.5 if (u, v) in matching or (v, u) in matching else 1.0 for u, v in B.edges()] # matching edges thicker

    nx.draw(B, pos, with_labels=True, node_color="lightgray", edge_color=edge_colors,
            width=edge_widths, node_size=2000, font_size=10, ax=ax) #Draws the full graph
    nx.draw_networkx_edge_labels(B, pos, edge_labels=edge_labels, font_size=9, ax=ax) #Displays edge labels

    st.pyplot(fig)

if __name__ == "__main__":
    main()
