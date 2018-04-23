cat sourcefiles | xargs cat | sed '/^\s*$/d' | wc -l
