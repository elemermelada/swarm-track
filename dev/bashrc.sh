source /etc/bash_completion.d/git-prompt
export GIT_PS1_SHOWDIRTYSTATE=1
export PS1='\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w \[\033[93m\]$(__git_ps1 "[%s]")\[\033[00m\]\$ '

# This must go in the end /shrug
sleep 1
conda activate tudat-space