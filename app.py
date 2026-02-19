import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Data Cleaner", layout="wide")

st.title("📊 Data Cleaner - Excel/CSV Editor")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload File")
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx", "csv", "xls"])

if uploaded_file is None:
    st.info("👈 Please upload an Excel or CSV file to get started!")
else:
    # Read the file
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File loaded successfully! ({df.shape[0]} rows, {df.shape[1]} columns)")
        
        # Create tabs for different operations
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["📋 View Data", "🗑️ Delete Columns", "❌ Delete Rows", "🔄 Remove Duplicates", "✏️ Edit Data", "⬇️ Download"]
        )
        
        # Tab 1: View Data
        with tab1:
            st.subheader("Current Data")
            st.dataframe(df, use_container_width=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", df.shape[0])
            with col2:
                st.metric("Total Columns", df.shape[1])
            with col3:
                st.metric("Total Cells", df.shape[0] * df.shape[1])
        
        # Tab 2: Delete Columns
        with tab2:
            st.subheader("Delete Columns")
            columns_to_delete = st.multiselect(
                "Select columns to delete",
                options=df.columns,
                key="delete_cols"
            )
            
            if columns_to_delete:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Delete Selected Columns", key="btn_del_cols"):
                        df = df.drop(columns=columns_to_delete)
                        st.success(f"✅ Deleted {len(columns_to_delete)} column(s)")
                        st.rerun()
                with col2:
                    st.info(f"Will delete: {', '.join(columns_to_delete)}")
        
        # Tab 3: Delete Rows
        with tab3:
            st.subheader("Delete Rows")
            st.write("Select rows to delete by index:")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                delete_method = st.radio("Delete by:", ["Index", "Condition"])
            
            if delete_method == "Index":
                rows_to_delete = st.multiselect(
                    "Select row indices to delete",
                    options=range(len(df)),
                    key="delete_rows_idx"
                )
                
                if rows_to_delete:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❌ Delete Selected Rows", key="btn_del_rows"):
                            df = df.drop(df.index[rows_to_delete])
                            df = df.reset_index(drop=True)
                            st.success(f"✅ Deleted {len(rows_to_delete)} row(s)")
                            st.rerun()
                    with col2:
                        st.info(f"Will delete: rows {rows_to_delete}")
            
            else:
                st.write("Delete rows where:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    condition_column = st.selectbox("Column", df.columns)
                with col2:
                    condition_type = st.selectbox("Condition", ["equals", "contains", "is empty", "is not empty"])
                with col3:
                    if condition_type != "is empty" and condition_type != "is not empty":
                        condition_value = st.text_input("Value")
                    else:
                        condition_value = None
                
                if st.button("❌ Delete Rows by Condition", key="btn_del_condition"):
                    if condition_type == "equals":
                        mask = df[condition_column] == condition_value
                    elif condition_type == "contains":
                        mask = df[condition_column].astype(str).str.contains(condition_value)
                    elif condition_type == "is empty":
                        mask = df[condition_column].isna() | (df[condition_column] == "")
                    else:  # is not empty
                        mask = ~(df[condition_column].isna() | (df[condition_column] == ""))
                    
                    rows_to_remove = mask.sum()
                    df = df[~mask]
                    df = df.reset_index(drop=True)
                    st.success(f"✅ Deleted {rows_to_remove} row(s)")
                    st.rerun()
        
        # Tab 4: Remove Duplicates
        with tab4:
            st.subheader("Remove Duplicate Rows")
            
            col1, col2 = st.columns(2)
            with col1:
                subset_cols = st.multiselect(
                    "Consider duplicates based on (leave empty for all columns):",
                    options=df.columns,
                    key="dup_cols"
                )
            with col2:
                keep_option = st.radio("Keep:", ["First", "Last"], horizontal=True)
            
            duplicates_count = df.duplicated(subset=subset_cols if subset_cols else None).sum()
            st.info(f"Found {duplicates_count} duplicate row(s)")
            
            if duplicates_count > 0:
                if st.button("🔄 Remove Duplicates", key="btn_dup"):
                    keep = "first" if keep_option == "First" else "last"
                    df = df.drop_duplicates(subset=subset_cols if subset_cols else None, keep=keep)
                    df = df.reset_index(drop=True)
                    st.success(f"✅ Removed {duplicates_count} duplicate row(s)")
                    st.rerun()
        
        # Tab 5: Edit Data
        with tab5:
            st.subheader("Edit Data")
            
            edit_method = st.radio("Edit method:", ["Edit specific cell", "Edit column", "Find & Replace"])
            
            if edit_method == "Edit specific cell":
                col1, col2, col3 = st.columns(3)
                with col1:
                    row_idx = st.number_input("Row index", min_value=0, max_value=len(df)-1)
                with col2:
                    col_name = st.selectbox("Column", df.columns)
                with col3:
                    new_value = st.text_input("New value")
                
                if st.button("✏️ Update Cell"):
                    df.at[row_idx, col_name] = new_value
                    st.success(f"✅ Updated {col_name}[{row_idx}]")
                    st.rerun()
            
            elif edit_method == "Edit column":
                col_to_edit = st.selectbox("Select column to edit", df.columns)
                st.write(f"Current values in '{col_to_edit}':")
                st.dataframe(df[[col_to_edit]], use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    find_value = st.text_input("Find value")
                with col2:
                    replace_value = st.text_input("Replace with")
                
                if st.button("🔄 Replace in Column"):
                    df[col_to_edit] = df[col_to_edit].astype(str).str.replace(find_value, replace_value)
                    st.success(f"✅ Updated column '{col_to_edit}'")
                    st.rerun()
            
            else:  # Find & Replace
                col1, col2 = st.columns(2)
                with col1:
                    find_text = st.text_input("Find (across all data)")
                with col2:
                    replace_text = st.text_input("Replace with (across all data)")
                
                if st.button("🔍 Find & Replace All"):
                    df = df.astype(str).replace(find_text, replace_text)
                    st.success("✅ Find & Replace completed")
                    st.rerun()
            
            st.divider()
            st.subheader("Preview Updated Data")
            st.dataframe(df, use_container_width=True)
        
        # Tab 6: Download
        with tab6:
            st.subheader("Download Cleaned Data")
            
            download_format = st.radio("Select format:", ["Excel (.xlsx)", "CSV (.csv)"], horizontal=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if download_format == "Excel (.xlsx)":
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Cleaned Data')
                    output.seek(0)
                    
                    st.download_button(
                        label="⬇️ Download as Excel",
                        data=output.getvalue(),
                        file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    output = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download as CSV",
                        data=output,
                        file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                st.info(f"📊 Data shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
