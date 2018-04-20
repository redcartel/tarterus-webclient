cat sourcefiles | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l
