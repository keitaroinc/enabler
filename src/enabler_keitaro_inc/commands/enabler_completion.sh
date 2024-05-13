_enabler_complete() {
    local cur_word prev_word

    # Get the current and previous words
    cur_word="${COMP_WORDS[COMP_CWORD]}"
    prev_word="${COMP_WORDS[COMP_CWORD-1]}"

    case "$prev_word" in
        "enabler") # noqa
            COMPREPLY=( $(compgen -W "apps kind preflight platform setup version" -- "$cur_word") )
            ;;
        "apps")
            COMPREPLY=( $(compgen -W "namespace" -- "$cur_word") )
            ;;
        "platform")
            COMPREPLY=( $(compgen -W "init info keys release version" -- "$cur_word") )
            ;;
        "kind")
            COMPREPLY=( $(compgen -W "create delete status start stop" -- "$cur_word") )
            ;;
        "setup")
            COMPREPLY=( $(compgen -W "init metallb istio" -- "$cur_word") )
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

complete -F _enabler_complete enabler