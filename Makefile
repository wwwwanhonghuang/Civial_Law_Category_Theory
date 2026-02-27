PROJECT_ROOT := $(realpath .)


install_python_dependencies:
	pip install python-docx

install_unix_dependencies:
	sudo apt-get install antiword catdoc


generate_raws_file_list:
	cd $(PROJECT_ROOT) && \
	python -m scripts.list_files --dir ./data/raw_laws --output data/titles_raw_laws.txt

vote_raw_laws:
	cd $(PROJECT_ROOT) && \
	python -m scripts.vote_items --file_list \
		./data/raw_law_selection/titles_selected_laws_chatgpt5.2.txt \
		./data/raw_law_selection/titles_selected_laws_claud.txt \
		./data/raw_law_selection/titles_selected_laws_deepseek.txt \
		./data/raw_law_selection/titles_selected_laws_deli.txt \
		./data/raw_law_selection/titles_selected_laws_doubao.txt \
		./data/raw_law_selection/titles_selected_laws_gemini.txt \
		--output ./data/raw_law_selection/titles_selected_laws.txt

convert_raw_law_to_plaintext:
	cd $(PROJECT_ROOT) && \
	python -m scripts.convert_raw_law_to_plaintext --file_titles_selected_laws ./data/raw_law_selection/titles_selected_laws.txt \
								 --output_folder ./data/law_text --raw_laws_folder ./data/raw_laws --output_merged_file
