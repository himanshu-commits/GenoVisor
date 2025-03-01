import tkinter as tk
from tkinter import messagebox, ttk
from Bio import Entrez, SeqIO
from Bio.Seq import Seq
from bs4 import BeautifulSoup
import requests
import time
import re

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time} seconds")
        return result
    return wrapper

@measure_execution_time
def fetch_sequence(accession_number):
    try:
        Entrez.email = "himanshu.code11@gmail.com"
        handle = Entrez.efetch(db="nucleotide",
                               id=accession_number,
                               rettype="gb",
                               retmode="text")
        record = SeqIO.read(handle, "genbank")
        dna_sequence = str(record.seq)
        protein_sequence = str(record.seq.translate())
        definition = record.description
        handle.close()
        return dna_sequence, protein_sequence, definition
    except Exception as e:
        return None, None, str(e)
@measure_execution_time
def fetch_expasy_info(protein_sequence):
    try:
        url = "https://web.expasy.org/cgi-bin/protparam/protparam"
        data = {"sequence": protein_sequence, "variant": "human"}
        response = requests.post(url, data=data)
        response.raise_for_status()  # Check for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the element containing the required information
        pre_elements = soup.find_all('pre')

        parameters = {'amino_acids': 'N/A', 'molecular_weight': 'N/A', 'theoretical_pi': 'N/A',
                      'neg_charged_residues': 'N/A', 'pos_charged_residues': 'N/A',
                      'formula': 'N/A', 'total_atoms': 'N/A', 'aliphatic_index': 'N/A',
                      'gravy': 'N/A', 'instability_index': 'N/A'}

        for pre_element in pre_elements:
            text = pre_element.text
            if 'Number of amino acids:' in text:
                match = re.search(r'Number of amino acids: (\d+)', text)
                if match:
                    parameters['amino_acids'] = match.group(1)

            if 'Molecular weight:' in text:
                match = re.search(r'Molecular weight: ([\d.]+)', text)
                if match:
                    parameters['molecular_weight'] = match.group(1)

            if 'Theoretical pI:' in text:
                match = re.search(r'Theoretical pI: ([\d.]+)', text)
                if match:
                    parameters['theoretical_pi'] = match.group(1)

            if 'Total number of negatively charged residues (Asp + Glu):' in text:
                match = re.search(r'Total number of negatively charged residues \(Asp \+ Glu\): (\d+)', text)
                if match:
                    parameters['neg_charged_residues'] = match.group(1)

            if 'Total number of positively charged residues (Arg + Lys):' in text:
                match = re.search(r'Total number of positively charged residues \(Arg \+ Lys\): (\d+)', text)
                if match:
                    parameters['pos_charged_residues'] = match.group(1)

            if 'Aliphatic index:' in text:
                match = re.search(r'Aliphatic index: ([\d.]+)', text)
                if match:
                    parameters['aliphatic_index'] = match.group(1)
            
            if 'Grand average of hydropathicity (GRAVY):' in text:
                match = re.search(r'Grand average of hydropathicity \(GRAVY\): ([\d.-]+)', text)
                if match:
                    parameters['gravy'] = match.group(1)

            if 'Instability index:' in text:
                match = re.search(r'Instability index: ([\d.-]+)', text)
                if match:
                    parameters['instability_index'] = match.group(1)

# ...


            if 'Formula:' in text:
                match = re.search(r'Formula: (.+)', text)
                if match:
                    parameters['formula'] = match.group(1)

            if 'Total number of atoms:' in text:
                match = re.search(r'Total number of atoms: (\d+)', text)
                if match:
                    parameters['total_atoms'] = match.group(1)

        # Remove 'N/A' values
        parameters = {key: value for key, value in parameters.items() if value != 'N/A'}

        return parameters
    except requests.exceptions.RequestException as e:
        print(f"Error fetching information from ExPASy ProtParam: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
@measure_execution_time

def copy_to_clipboard(sequence_type, sequence_text_widget):
    sequence_to_copy = sequence_text_widget.get("1.0", "end-1c")

    # Copy sequence to clipboard
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(sequence_to_copy)  # Append the sequence to clipboard
    root.update()  # Update clipboard
    root.destroy()  # Destroy the hidden window

    messagebox.showinfo("Copy to Clipboard",
                        f"{sequence_type} sequence copied to clipboard")

@measure_execution_time
def on_fetch_sequence():
    # Show loading sign
    loading_label.config(text="Fetching sequence...", foreground="blue")
    root.update()

    accession_number = accession_entry.get()
    dna_sequence, protein_sequence, definition = fetch_sequence(accession_number)

    # Hide loading sign
    loading_label.config(text="", foreground="black")

    if dna_sequence and protein_sequence:
        dna_text.delete(1.0, tk.END)
        dna_text.insert(tk.END, dna_sequence)

        protein_text.delete(1.0, tk.END)
        protein_text.insert(tk.END, protein_sequence)

        result_label.config(text=f"Definition: {definition}")
    else:
        result_label.config(text=f"Error fetching sequence. Check accession number: {definition}")

@measure_execution_time
def translate_to_protein():
    # Get the DNA sequence from the DNA text area and remove non-DNA characters
    dna_sequence = re.sub('[^ACGTacgt]', '', dna_text.get("1.0", tk.END))

    # Check if the DNA sequence is not empty
    if dna_sequence:
        try:
            # Translate DNA to protein
            protein_sequence = str(Seq(dna_sequence).translate())
            
            # Update the Protein Sequence column
            protein_text.delete(1.0, tk.END)
            protein_text.insert(tk.END, protein_sequence)
        except Exception as e:
            messagebox.showinfo("Translation Error", f"Error during translation: {e}")
    else:
        messagebox.showinfo("No DNA Sequence", "Enter a DNA sequence first.")
@measure_execution_time
def reset_accession_number():
    accession_entry.delete(0, tk.END)
@measure_execution_time
def reset_sequence():
    # Clear the DNA sequence field
    dna_text.delete(1.0, tk.END)

    # Clear the Protein sequence field
    protein_text.delete(1.0, tk.END)
@measure_execution_time 
def reset_protein_and_parameters():
    # Clear Protein sequence and parameters
   # protein_text.delete(1.0, tk.END)
    #protein_entry.config(state=tk.NORMAL)
    protein_entry.delete(0 ,tk.END)
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.config(state=tk.DISABLED)
@measure_execution_time  
def generate_parameters():
    protein_sequence = protein_entry.get()
    parameters = fetch_expasy_info(protein_sequence)

    if parameters is not None:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        for key, value in parameters.items():
            result_text.insert(tk.END, f"{key}: {value}\n")
        result_text.config(state=tk.DISABLED)
    else:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Error fetching information. Check your input.\n")
        result_text.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("BioTransPro")

style = ttk.Style()
style.configure("Colorful.TButton", foreground="white", background="#4CAF50", font=("Helvetica", 10, "bold"))
# Create and place widgets
fetch_button = ttk.Button(root,
                          text="Fetch Sequence",
                          command=on_fetch_sequence)
fetch_button.grid(row=0, column=0, padx=10, pady=10)
loading_label = ttk.Label(root, text="", foreground="black")
loading_label.grid(row=1, column=1, padx=10, pady=10)
reset_accession_button = ttk.Button(root,
                                    text="Reset Accession",
                                    command=reset_accession_number)
reset_accession_button.grid(row=0, column=1, padx=10, pady=10)

accession_label = ttk.Label(root, text="Accession Number:")
accession_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")

accession_entry = ttk.Entry(root, width=20)
accession_entry.grid(row=0, column=4, padx=10, pady=10)

result_label = ttk.Label(root, text="")
result_label.grid(row=1, column=0, columnspan=5, pady=10)

# Create a frame for DNA and Protein sequences
sequence_frame = ttk.Frame(root)
sequence_frame.grid(row=2, column=0, columnspan=5, padx=10, pady=10)

dna_label = ttk.Label(sequence_frame, text="DNA Sequence:")
dna_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

dna_text = tk.Text(sequence_frame, height=5, width=40)
dna_text.grid(row=1, column=0, padx=10, pady=10)

# Add a vertical scrollbar for the DNA sequence text
dna_scrollbar = ttk.Scrollbar(sequence_frame, command=dna_text.yview)
dna_scrollbar.grid(row=1, column=1, sticky='nsew')
dna_text['yscrollcommand'] = dna_scrollbar.set

protein_label = ttk.Label(sequence_frame, text="Protein Sequence:")
protein_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

protein_text = tk.Text(sequence_frame, height=5, width=40)
protein_text.grid(row=1, column=2, padx=10, pady=10)

# Add a vertical scrollbar for the Protein sequence text
protein_scrollbar = ttk.Scrollbar(sequence_frame, command=protein_text.yview)
protein_scrollbar.grid(row=1, column=3, sticky='nsew')
protein_text['yscrollcommand'] = protein_scrollbar.set

translate_button = ttk.Button(sequence_frame,
                              text="Translate to Protein",
                              command=translate_to_protein)
translate_button.grid(row=2, column=1, padx=10, pady=10)

copy_dna_button = ttk.Button(sequence_frame,
                             text="Copy DNA Seq to Clipboard",
                             command=lambda: copy_to_clipboard("DNA", dna_text))
copy_dna_button.grid(row=2, column=0, padx=10, pady=10)

copy_protein_button = ttk.Button(sequence_frame,
                                 text="Copy Protein Seq to Clipboard",
                                 command=lambda: copy_to_clipboard("Protein", protein_text))
copy_protein_button.grid(row=2, column=3, padx=10, pady=10)



# Create a frame for protein entry and parameter generation
protein_frame = ttk.Frame(root)
protein_frame.grid(row=3,column=0, columnspan=5, padx=10, pady=10)

protein_label = ttk.Label(protein_frame, text="Protein Sequence:")
protein_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

protein_entry = tk.Entry(protein_frame, width=40)
protein_entry.grid(row=0, column=1, padx=10, pady=10)
reset_sequence_button = ttk.Button(sequence_frame,
                                    text="Reset Sequence",
                                    command=reset_sequence)
reset_sequence_button.grid(row=2, column=2, padx=10, pady=10)

reset_protein_button = ttk.Button(root, text="Reset Parameters", command=reset_protein_and_parameters)
reset_protein_button.grid(row=3, column=4, padx=10, pady=10)

generate_button = ttk.Button(protein_frame,
                             text="Generate Parameters",
                             command=generate_parameters)
generate_button.grid(row=0, column=2, padx=10, pady=10)

result_text = tk.Text(protein_frame, height=12, width=40, state=tk.DISABLED)
result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Run the Tkinter event loop
root.mainloop()
