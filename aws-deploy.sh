#!/bin/bash
export EC2_PRIVATE_KEY=/etc/ec2-pkey.pem
export EC2_CERT=/etc/ec2-cert.pem

function kill_spiders {
	kill -9 $(pgrep -P $$ | tr "\n" " ")
	kill -9 $(pgrep -P $$ | tr "\n" " ")
}
trap kill_spiders SIGINT SIGTERM EXIT

source env/bin/activate

mkdir -p /mnt/cache
mkdir -p /mnt/feeds

ts=$(date +%s)
mkdir -p /mnt/log/$ts

for file in prawler/sites/*.json; do
        site=${file:14:-5}
	scrapy crawl product -a site=$file >/mnt/log/${ts}/${site}.log 2>&1 &
done

wait
echo '*** all spiders done, saving cache to EBS volume'

aws_zone=$(ec2metadata --availability-zone)
aws_region=$(echo $aws_zone | sed -e 's/.$//')
instance=$(ec2metadata --instance-id)

tar -C /mnt -cpzf /mnt/cache.tar.gz cache
tar -C /mnt -cpzf /mnt/feeds.tar.gz feeds
tar -C /mnt -cpzf /mnt/log.tar.gz log

size=$(du -BG -c /mnt/*.tar.gz | tail -n 1 | grep -Eo '^[0-9]+')
size=$((size + size/10))

if [[ $size -le 0 || $size -gt 200 ]]; then
	echo "!!! requested cache EBS volume size (${size}G) is out of range (1-200G)"
	exit 1
fi

vol=$(ec2-create-volume --region $aws_region -z $aws_zone --size $size | cut -f2)
ec2-create-tags $vol --tag "Name=crawler-cache" --region $aws_region
ec2-attach-volume --region $aws_region $vol -i $instance -d /dev/xvdg

for (( a = 0; a < 5; a = a+1 )); do
	sleep 5
	stat=$(ec2-describe-volumes --region $aws_region $vol | grep ATTACHMENT | cut -f5)
	echo $stat
	if [[ $stat == "attached" ]]; then
		break;
	fi
done

echo "*** attached $vol (${size}G) to /dev/xvdg"

mke2fs /dev/xvdg
mkdir -p /media/cache-vol
mount /dev/xvdg /media/cache-vol

dd if=/mnt/cache.tar.gz of=/media/cache-vol/cache.tar.gz bs=16M
dd if=/mnt/feeds.tar.gz of=/media/cache-vol/feeds.tar.gz bs=16M
dd if=/mnt/log.tar.gz of=/media/cache-vol/log.tar.gz bs=16M

umount /media/cache-vol
rm -r /media/cache-vol

sleep 5
snapshot=$(ec2-create-snapshot --region $aws_region $vol | cut -f2)

sleep 5
ec2-create-tags $snapshot --tag "Name=crawler-cache" --region $aws_region
ec2-detach-volume --region $aws_region $vol

sleep 10
ec2-delete-volume --region $aws_region $vol
