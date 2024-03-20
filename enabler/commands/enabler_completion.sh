_enabler_complete() {
    local cur_word prev_word commands

    # Get the current and previous words
    cur_word="${COMP_WORDS[COMP_CWORD]}"
    prev_word="${COMP_WORDS[COMP_CWORD-1]}"
    local categories="apps kind preflight platform setup version"

    case "$prev_word" in
        "enabler") # noqa
            commands="$categories"
            ;;
    esac

    # Initialize the variable to store previous words
    prev_words=""
    local apps="namespace"
    local kind="create delete status start stop"
    local platform="init info keys release version"
    local setup="init metallb istio"

    # Loop through previous words and concatenate them
    for ((i=1; i<COMP_CWORD; i++)); 
    do
        prev_words="${prev_words}${COMP_WORDS[i]} "
    done

    # Trim any trailing whitespace
    prev_words="${prev_words% }"

    case "$prev_words" in
        "enabler apps")
            commands="$commands $apps"
            ;;
        "enabler kind")
            commands="$commands $kind"
            ;;
        "enabler platform")
            commands="$commands $platform"
            ;;
        "enabler setup")
            commands="$commands $setup"
            ;;
    esac
    
    echo ""
    echo "$commands"

    if [[ "$cur_word" == "$prev_word"* ]]; then
        COMPREPLY=( $(compgen -W "$commands" -- "$cur_word") )
    fi
}

# Register _enabler_complete to provide completion for the enabler command
complete -F _enabler_complete enabler