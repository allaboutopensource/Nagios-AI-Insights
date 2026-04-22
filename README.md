# Nagios-AI-Insights


<img width="1723" height="518" alt="image" src="https://github.com/user-attachments/assets/39a972aa-759d-4c4e-bcc6-cf2353433705" />





you need to create commands : 

check_nagios_host_ai:    $USER1$/aws-creds.sh "$HOSTNAME$" "$HOSTSTATE$" "$HOSTOUTPUT$" "$HOSTSTATETYPE$" "host"

check_nagios_service_ai: $USER1$/aws-creds.sh "$HOSTNAME$" "$SERVICEDESC$" "$SERVICESTATE$" "$SERVICEOUTPUT$" "$SERVICESTATETYPE$" "service"	



You need to enable the event handler and map the Event handler as well on the host/service on the nagios XI 
