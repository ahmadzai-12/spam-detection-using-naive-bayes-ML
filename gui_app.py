"""
Email Spam Detection - Tkinter GUI Application
Provides a user-friendly desktop interface for spam detection
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from predict import SpamPredictor

class SpamDetectionGUI:
    """Desktop GUI application for spam detection"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Email Spam Detection System")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Load the model
        try:
            self.predictor = SpamPredictor()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.root.destroy()
            return
        
        # Setup GUI components
        self.setup_ui()
        
    def setup_ui(self):
        """Create all GUI elements"""
        
        # Title
        title_label = tk.Label(
            self.root, 
            text="📧 Email Spam Detection System", 
            font=("Arial", 20, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.root,
            text="Using Multinomial Naive Bayes with TF-IDF Vectorization",
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=5)
        
        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Input label
        input_label = tk.Label(
            input_frame,
            text="Enter Email Content:",
            font=("Arial", 12, "bold")
        )
        input_label.pack(anchor="w", pady=(0, 5))
        
        # Text input area
        self.text_input = scrolledtext.ScrolledText(
            input_frame,
            height=12,
            font=("Arial", 10),
            wrap=tk.WORD,
            relief=tk.GROOVE,
            borderwidth=2
        )
        self.text_input.pack(fill="both", expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Predict button
        self.predict_btn = tk.Button(
            button_frame,
            text="🔍 Detect Spam",
            command=self.predict_spam,
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.predict_btn.pack(side="left", padx=10)
        
        # Clear button
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_text,
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.clear_btn.pack(side="left", padx=10)
        
        # Sample button
        self.sample_btn = tk.Button(
            button_frame,
            text="📝 Load Sample",
            command=self.load_sample,
            font=("Arial", 12),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.sample_btn.pack(side="left", padx=10)
        
        # Result frame
        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=20, padx=20, fill="x")
        
        # Result label
        result_label = tk.Label(
            result_frame,
            text="Detection Result:",
            font=("Arial", 12, "bold")
        )
        result_label.pack(anchor="w")
        
        # Result display
        self.result_display = tk.Label(
            result_frame,
            text="Waiting for input...",
            font=("Arial", 14),
            bg="#ecf0f1",
            fg="#2c3e50",
            relief=tk.RAISED,
            padx=20,
            pady=20
        )
        self.result_display.pack(fill="x", pady=(5, 10))
        
        # Confidence display
        self.confidence_display = tk.Label(
            result_frame,
            text="",
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        self.confidence_display.pack()
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 9),
            relief=tk.SUNKEN,
            anchor="w"
        )
        self.status_bar.pack(side="bottom", fill="x")
        
    def predict_spam(self):
        """Predict if the entered email is spam"""
        email_text = self.text_input.get("1.0", tk.END).strip()
        
        if not email_text:
            messagebox.showwarning("Warning", "Please enter email content to analyze!")
            return
        
        # Update status
        self.status_bar.config(text="Analyzing email content...")
        self.root.update()
        
        try:
            # Make prediction
            result = self.predictor.predict_email(email_text)
            
            # Update result display
            if result['is_spam']:
                self.result_display.config(
                    text=f"⚠️ {result['label']} DETECTED! ⚠️",
                    bg="#e74c3c",
                    fg="white",
                    font=("Arial", 16, "bold")
                )
            else:
                self.result_display.config(
                    text=f"✅ {result['label']} - Safe Email ✅",
                    bg="#2ecc71",
                    fg="white",
                    font=("Arial", 16, "bold")
                )
            
            # Update confidence display
            self.confidence_display.config(
                text=f"Confidence: {result['confidence']:.2f}% | "
                     f"Spam Probability: {result['spam_probability']:.2f}% | "
                     f"Ham Probability: {result['ham_probability']:.2f}%"
            )
            
            # Update status
            self.status_bar.config(text="Analysis complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {str(e)}")
            self.status_bar.config(text="Error occurred")
    
    def clear_text(self):
        """Clear the input text area"""
        self.text_input.delete("1.0", tk.END)
        self.result_display.config(
            text="Waiting for input...",
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Arial", 14)
        )
        self.confidence_display.config(text="")
        self.status_bar.config(text="Cleared - Ready for new input")
    
    def load_sample(self):
        """Load a sample email for testing"""
        sample_emails = [
            "Congratulations! You've won a $1000 gift card. Click here to claim now! Limited time offer!",
            "Hi team, please find attached the quarterly report. Let me know if you have any questions.",
            "URGENT: Your PayPal account has been limited. Verify your account immediately to avoid suspension.",
            "Reminder: Our meeting scheduled for tomorrow at 2 PM has been moved to 3 PM."
        ]
        
        # Create a dialog to select sample
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Sample Email")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Choose a sample email:", font=("Arial", 12, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(dialog, height=8, font=("Arial", 10))
        for email in sample_emails:
            listbox.insert(tk.END, email[:80] + "..." if len(email) > 80 else email)
        listbox.pack(pady=10, padx=20, fill="both", expand=True)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                self.clear_text()
                self.text_input.insert("1.0", sample_emails[selection[0]])
                dialog.destroy()
        
        tk.Button(dialog, text="Load Selected", command=on_select, bg="#3498db", fg="white").pack(pady=10)


def main():
    root = tk.Tk()
    app = SpamDetectionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()