import tkinter as tk
from tkinter import messagebox, ttk
from Bio import Entrez, SeqIO
from bs4 import BeautifulSoup
import requests
import re

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
    except Exception:
        return None, None, None

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


def save_and_copy_sequence(sequence_type, sequence_text_widget, filename):
    sequence_to_save = sequence_text_widget.get("1.0", "end-1c")

    try:
        with open(filename, "r") as file:
            existing_sequence = file.read()
            if existing_sequence.strip() == sequence_to_save.strip():
                messagebox.showinfo(
                    "Already Saved",
                    f"The {sequence_type} sequence is already saved in {filename}")
            else:
                with open(filename, "a") as file:
                    file.write("\n" + sequence_to_save)
                messagebox.showinfo("Save Successful",
                                    f"{sequence_type} sequence appended to {filename}")
    except FileNotFoundError:
        with open(filename, "w") as file:
            file.write(sequence_to_save)
        messagebox.showinfo("Save Successful",
                            f"{sequence_type} sequence saved to {filename}")

    # Copy sequence to clipboard
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(sequence_to_save)  # Append the sequence to clipboard
    root.update()  # Update clipboard
    root.destroy()  # Destroy the hidden window

    messagebox.showinfo("Copy to Clipboard",
                        f"{sequence_type} sequence copied to clipboard")


def on_fetch_sequence():
    accession_number = accession_entry.get()
    dna_sequence, protein_sequence, definition = fetch_sequence(accession_number)
    if dna_sequence and protein_sequence:
        dna_text.delete(1.0, tk.END)
        dna_text.insert(tk.END, dna_sequence)

        protein_text.delete(1.0, tk.END)
        protein_text.insert(tk.END, protein_sequence)

        result_label.config(text=f"Definition: {definition}")
    else:
        result_label.config(
            text="Error fetching sequence. Check accession number.")

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
root.title("DNA to Protein Converter")

# Create and place widgets
fetch_button = ttk.Button(root,
                          text="Fetch Sequence",
                          command=on_fetch_sequence)
fetch_button.grid(row=0, column=0, padx=10, pady=10)

reset_button = ttk.Button(root,
                          text="Reset",
                          command=lambda: result_label.config(text=""))
reset_button.grid(row=0, column=1, padx=10, pady=10)

accession_label = ttk.Label(root, text="Accession Number:")
accession_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

accession_entry = ttk.Entry(root, width=20)
accession_entry.grid(row=0, column=3, padx=10, pady=10)

result_label = ttk.Label(root, text="")
result_label.grid(row=1, column=0, columnspan=4, pady=10)

# Create a frame for DNA and Protein sequences
sequence_frame = ttk.Frame(root)
sequence_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

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

copy_dna_button = ttk.Button(sequence_frame,
                             text="Save and Copy DNA",
                             command=lambda: save_and_copy_sequence(
                                 "DNA", dna_text, "dna_sequence.txt"))
copy_dna_button.grid(row=2, column=0, padx=10, pady=10)

copy_protein_button = ttk.Button(
    sequence_frame,
    text="Save and Copy Protein",
    command=lambda: save_and_copy_sequence("Protein", protein_text,
                                           "protein_sequence.txt"))
copy_protein_button.grid(row=2, column=2, padx=10, pady=10)

# Create a frame for protein entry and parameter generation
protein_frame = ttk.Frame(root)
protein_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

protein_label = ttk.Label(protein_frame, text="Protein Sequence:")
protein_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

protein_entry = tk.Entry(protein_frame, width=40)
protein_entry.grid(row=0, column=1, padx=10, pady=10)

generate_button = ttk.Button(protein_frame,
                             text="Generate Parameters",
                             command=generate_parameters)
generate_button.grid(row=0, column=2, padx=10, pady=10)

result_text = tk.Text(protein_frame, height=12, width=40, state=tk.DISABLED)
result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Run the Tkinter event loop
root.mainloop()
