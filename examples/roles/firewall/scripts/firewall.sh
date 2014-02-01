#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

apt-get -y install shorewall shorewall6 fail2ban

/etc/init.d/fail2ban stop

for i in /etc/shorewall/shorewall.conf /etc/shorewall6/shorewall6.conf ; do
    sed -e s:"^BLACKLISTNEWONLY=No":"BLACKLISTNEWONLY=Yes": -i $i
done

for i in /etc/default/shorewall /etc/default/shorewall6 ; do
    sed -e s:"^startup=0":"startup=1": -i $i
done

for i in shorewall shorewall6 ; do
    update-rc.d $i defaults
    /etc/init.d/$i start
done

sed -e s:"^banaction = iptables-multiport$":"banaction = shorewall": -i /etc/fail2ban/jail.conf

/etc/init.d/fail2ban start
