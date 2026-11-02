
import streamlit as st
import subprocess
import tempfile
import hashlib
from pathlib import Path

OPENSSL = r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe"

st.set_page_config(
    page_title="File Encryption & Decryption",
    page_icon="🔐",
    layout="centered"
)

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def run_openssl(mode, file_data, password):
    with tempfile.TemporaryDirectory() as folder:
        input_path = Path(folder) / "input_file"
        output_path = Path(folder) / "output_file"

        input_path.write_bytes(file_data)

        command = [
            OPENSSL, "enc",
            "-aes-256-cbc",
            "-pbkdf2"
        ]

        if mode == "encrypt":
            command.append("-salt")
        else:
            command.append("-d")

        command += [
            "-in", str(input_path),
            "-out", str(output_path),
            "-pass", "stdin"
        ]

        result = subprocess.run(
            command,
            input=(password + "\n").encode(),
            capture_output=True
        )

        if result.returncode != 0:
            error = result.stderr.decode(errors="replace")
            raise ValueError(error or "OpenSSL operation failed.")

        return output_path.read_bytes()


st.title("🔐 File Encryption & Decryption")
st.caption("Secure file protection using AES-256-CBC and PBKDF2")

st.info(
    "This application uses OpenSSL to encrypt and decrypt files "
    "with password-based key derivation."
)

tab1, tab2 = st.tabs(["🔒 Encrypt File", "🔓 Decrypt File"])

with tab1:
    st.subheader("File Encryption")

    uploaded_file = st.file_uploader(
        "Upload the original file",
        type=["txt"],
        key="encrypt_file"
    )

    encrypt_password = st.text_input(
        "Enter encryption password",
        type="password",
        key="encrypt_password"
    )

    if st.button("Encrypt File", type="primary"):
        if uploaded_file is None:
            st.error("Please upload a file.")
        elif not encrypt_password:
            st.error("Please enter a password.")
        else:
            try:
                original_data = uploaded_file.getvalue()
                encrypted_data = run_openssl(
                    "encrypt", original_data, encrypt_password
                )

                st.success("File encrypted successfully!")

                st.write("Original SHA-256:")
                st.code(sha256(original_data))

                st.write("Encrypted file SHA-256:")
                st.code(sha256(encrypted_data))

                st.download_button(
                    "Download Encrypted File",
                    data=encrypted_data,
                    file_name="encrypted_file.enc",
                    mime="application/octet-stream"
                )

            except Exception as e:
                st.error(f"Encryption failed: {e}")


with tab2:
    st.subheader("File Decryption")

    encrypted_file = st.file_uploader(
        "Upload the encrypted file",
        type=["enc"],
        key="decrypt_file"
    )

    decrypt_password = st.text_input(
        "Enter decryption password",
        type="password",
        key="decrypt_password"
    )

    if st.button("Decrypt File", type="primary"):
        if encrypted_file is None:
            st.error("Please upload an encrypted file.")
        elif not decrypt_password:
            st.error("Please enter the password.")
        else:
            try:
                encrypted_data = encrypted_file.getvalue()

                recovered_data = run_openssl(
                    "decrypt", encrypted_data, decrypt_password
                )

                st.success("File decrypted successfully!")

                st.write("Recovered file SHA-256:")
                st.code(sha256(recovered_data))

                st.download_button(
                    "Download Recovered File",
                    data=recovered_data,
                    file_name="recovered.txt",
                    mime="text/plain"
                )

            except Exception:
                st.error(
                    "Decryption failed. Check your password "
                    "and encrypted file."
                )

st.divider()

st.subheader("Project Information")
st.markdown("""
- **Algorithm:** AES-256-CBC
- **Key Derivation:** PBKDF2
- **Cryptographic Tool:** OpenSSL
- **Programming Language:** Python
- **Interface:** Streamlit
""")

st.caption("File Encryption and Decryption | Cryptography Project")

