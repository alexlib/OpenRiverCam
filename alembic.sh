#!/bin/bash
### ALEMBIC MIGRATION PIPELINE TO DOCKER INSTANCE ###
# Bash script to forward alembic commands to the portal via docker image
# this must be run while the docker-compose services are running. So first
# do docker-compose up if you haven't done that yet.
man_help(){
    echo '#############################################'
    echo 'Alembic command via docker instance of portal'
    echo '#############################################'
    echo 'Bash scripts to perform alembic operators on the OpenRiverCam portal'
    echo ''
    echo '* To run this script, the docker-compose services should be running'
    echo '* The script runs with all alembic commands. Example arguments are given below'
    echo '* To correctly forward all arguments, always place them between single quotes'
    echo '* Run scripts as follows:'
    echo ''
    echo -e './alembic.sh \x27<alembic args>\x27'
    echo ''
    echo ''
    echo 'Example usages:'
    echo ''
    echo -e '        ./alembic.sh \x27--help\x27'
    echo '                         help page of alembic'
    echo ''
    echo -e '        ./alembic.sh \x27upgrade head\x27'
    echo '                         generate tables from scratch with a new deployment'
    echo ''
    echo -e '        ./alembic.sh \x27stamp head\x27'
    echo '                         Stamp database to most current version'
    echo ''
    echo -e '        ./alembic.sh \x27revision --autogenerate -m "name of change"\x27'
    echo '                         prepares a new revision script from recent model changes with comment "name of change"'
    echo ''
    exit 0
}

exec_alembic(){
    echo 'Performing alembic operations with args: ' $*
    docker exec -it openrivercam_portal_1 bash -c "alembic $*"
#    docker exec -it openrivercam_portal_1 bash -c "echo $*"

}

main() {
    # if no parameters display help
    if [ -z "$@" ]                      ; then man_help                          ;
#    elif [ "$@" == "--help" ]           ; then man_help                          ;
    else exec_alembic $@                   ;
    fi
}

main "$@"
#sudo ufw enable
exit 0


#docker exec -it openrivercam_portal_1 bash -c "echo $PWD"