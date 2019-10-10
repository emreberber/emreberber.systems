<p>"Digital Ocean ve Google Cloud ile Authoritative Only Bind DNS" başlıklı yazımda, linkini <a href="https://emreberber.systems/digital-ocean-ve-google-cloud-ile-authoritative-only-bind-dns/">buraya</a> bırakayım, Ubuntu Server 16.04 üzerinde kurmuş olduğum Bind DNS Sunuculardan bahsetmiştim. Master Bind Server DigitalOcean'da yer alırken, Slave Bind Server Google Cloud üzerinde yer almakta. Bu yazıda Slave Sunucunun Microsoft'un bulut platformu olan <strong>Azure</strong>'a taşınma adımlarını anlatmaya çalışacağım. Bu sefer Ubuntu yerine <strong>RHEL</strong> tabanlı <strong>CentOS</strong> dağıtımını tercih ettim.</p><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/microsoft-azure11.png" class="kg-image"></figure><p>Azure ve CentOS tercih etmemin herhangi özel bir sebebi yok. Azure 12 ay için 200$ kredi veriyor. CentOS'u da Ubuntu dışına çıkmak için belirledim. <strong>azure.microsoft.com</strong> adresinden kayıt vs adımlarını geçtikten sonra işimizi görecek olan microsoftumsu bir tasarıma sahip sayfaya yönlendiriliyoruz.</p><hr><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/2019-02-04_10-25.png" class="kg-image"></figure><p>Lazım olan şey bir adet sanal makine. Azure Services başlığı altında ya da sağ menüde yer alan '<strong>Virtual machines</strong>' üzerinden ilerliyoruz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/2019-02-04_10-57.png" class="kg-image"></figure><p>Virtual machines ana sayfasında yeni bir sanal makine oluşturalım.</p><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/2019-02-04_11-04.png" class="kg-image"></figure><p>Resource group alanı oluşturmamızı zorunlu kılmış, 'Create new' ile <strong>azure-vm</strong> ismini verdim. Sanırım bunu, oluşturacağımız VM'leri gruplandırmak için istiyor. Ardından makineye isim verdik ki bu önemli. Gidip de sunucuya sanal_makine_61 gibi saçma isimler vermiyoruz arkadaşlar.</p><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/2019-02-04_11-43.png" class="kg-image"></figure><p>Biraz aşağı indikten sonra 'İmage' olarak ben <strong>Centos 7.5'</strong>i tercih ettim. 'Size' tarafında DNS Sunucumuz için 1 GB Ram yeterlidir. </p><p>Diğer sekmelerde şuanlık bizlik bir şey yok. 'Review + create' butonu ile makineyi oluşturuyoruz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/2019-02-04_11-57.png" class="kg-image"></figure><p>Review yapmışız ama create yapamamışız :) yaptıklarımızın geçerli olduğunu belirtmiş ve sanırım şimdi create diyebilirim. 2-3 dk içinde makineyi oluşturduktan sonra 'Start' ile başlatalım.</p><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/2019-02-04_12-06.png" class="kg-image"></figure><p>Daha sonra makinenin aldığı IP adresini, Dynamic IP'den <strong>Static IP</strong>'e çevirmemiz gerekiyor. Bu işlemi 'Home' sayfasında yer alan tabloda, type'ı 'Public IP Address' olan linke tıkladıktan sonra açılan sayfada 'Static' olarak belirtiyoruz. Ardından 'Save' yapmayı unutmuyoruz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/2019-02-04_12-10.png" class="kg-image"></figure><p>Makineye <strong>SSH </strong>ile bağlanabilmek için 'Networking' sekmesinden 22.porta izin vermemiz gerekiyor.</p><figure class="kg-card kg-image-card"><img src="/content/images/2019/02/2019-02-04_12-36.png" class="kg-image"></figure><p>'Add inbound port rule' butonuna tıklayarak açılan kısımda sadece port numarasını 22 ve name'i ssh olarak güncelledim. Burada port numarasının 22 olması önemli. Bu işlemlerin ardından bilgisayarımın tterminalinden ssh bağlantısını gerçekleştirebilmekteyim.</p><hr><pre><code class="language-bash">$ ssh user@ip_addr
</code></pre>
<p>Olmazsa olmaz :</p><pre><code class="language-bash">$ sudo yum update
$ sudo yum upgrade
</code></pre>
<p>Bind kurulumu için,</p><pre><code>$ sudo yum install bind bind-utils
</code></pre>
<pre><code>$ sudo vim /etc/named.conf
</code></pre>
<pre><code class="language-wiki">options {
        listen-on port 53 { any; };
        listen-on-v6 port 53 { any; };
        directory       &quot;/var/named&quot;;
        dump-file       &quot;/var/named/data/cache_dump.db&quot;;
        statistics-file &quot;/var/named/data/named_stats.txt&quot;;
        memstatistics-file &quot;/var/named/data/named_mem_stats.txt&quot;;
        recursing-file  &quot;/var/named/data/named.recursing&quot;;
        secroots-file   &quot;/var/named/data/named.secroots&quot;;
        allow-query     { any; };
     
        recursion no;

        dnssec-enable yes;
        dnssec-validation yes;

        /* Path to ISC DLV key */
        bindkeys-file &quot;/etc/named.iscdlv.key&quot;;

        managed-keys-directory &quot;/var/named/dynamic&quot;;

        pid-file &quot;/run/named/named.pid&quot;;
        session-keyfile &quot;/run/named/session.key&quot;;
};
</code></pre>
<p>Burada <strong>listen-on port 53</strong> ve <strong>listen-on-v6 port 53 </strong>satırlarını <strong>any</strong> yaptıktan sonra <strong>recursion</strong> kısmını <strong>no</strong> olarak değiştiriyoruz.</p><pre><code>$ sudo vim /etc/named.rfc1912.zones 
</code></pre>
<pre><code class="language-wiki">zone &quot;emreberber.systems&quot; IN {
        type slave;
        file &quot;slaves/emreberber.systems&quot;;
        masters { 165.227.137.94; };  // Master IP
};

zone &quot;137.227.165.in-addr.arpa&quot; {
        type slave;
        file &quot;db.165.227.137&quot;;
        masters { 165.227.137.94; };  // Master IP
};
</code></pre>
<p>satırlarını ekledim.</p><pre><code>sudo systemctl enable named
sudo systemctl start named
</code></pre>
<p>Bind servisi CentOS'da <strong>named</strong> adı ile çağırılıyor. İlk önce bu servisi enable edip ardından başlattık. start yerine status yazınca da servisin ne durumda olduğunu gösterir. Slave Bind Server'ın Master ile bağlantı kurabilmesi için Master Sunucu'da Slave'in IP Adresini güncellememiz gerekiyor. Şimdi Master'dan devam ediyoruz.</p><pre><code>$ sudo vim /etc/bind/named.conf.local
</code></pre>
<pre><code class="language-wiki">zone &quot;emreberber.systems&quot; {
        type master;
        file &quot;/etc/bind/zones/db.emreberber.systems&quot;;
        allow-transfer { 40.121.48.54; };  // New Slave IP
};

zone &quot;137.227.165.in-addr.arpa&quot; {
        type master;
        file &quot;/etc/bind/zones/db.165.227.137&quot;;
        allow-transfer { 40.121.48.54; };  // New Slave IP
};
</code></pre>
<pre><code>sudo vim /etc/bind/zones/db.165.227.137
</code></pre>
<pre><code class="language-wiki">;
; BIND reverse data file for local loopback interface
;
$TTL    600
@       IN      SOA     emreberber.systems. admin.emreberber.systems. (
                     2019040100         ; Serial
                          28800         ; Refresh
                           7200         ; Retry
                         604800         ; Expire
                            600 )       ; Negative Cache TTL
;

; Name servers
        IN      NS      ns1.emreberber.systems.
        IN      NS      ns2.emreberber.systems.

; PTR records
94      IN      PTR     ns1.emreberber.systems.
54      IN      PTR     ns2.emreberber.systems.
178     IN      PTR     www.emreberber.systems.
39      IN      PTR     zabbix.emreberber.systems.
</code></pre>
<p>Zone dosyalarında yaptığımız her değişikliğin ardından <strong><strong>YYYYMMDDnn</strong> </strong>formatında olan <strong>Serial </strong>değerini güncellemeyi unutmuyoruz. Son olarak da az önce ssh için port 22'ye verdiğimiz izin gibi aynı şekilde port 53'e izin veriyoruz. Böylece gelen isteklere cevap verilebilsin. Slave ve Master için bind servislerini restart edebiliriz. Master için,</p><pre><code>$ sudo service bind9 restart
$ sudo sevice bind9 status
</code></pre>
<p>Yaptığımız değişiklikler sonucu herhangi bir hata durumu söz konusu olup olmadığının test etmek için,</p><pre><code>$ sudo named-checkconf
$ sudo named-checkzone emreberber.net /etc/bind/zones/db.emreberber.net
$ sudo named-checkzone 137.227.165.in-addr.arpa /etc/bind/zones/db.165.227.137
</code></pre>
<p>Slave için,</p><pre><code>$ sudo service named restart
$ sudo service named status
</code></pre>
<pre><code class="language-wiki">● named.service - Berkeley Internet Name Domain (DNS)
   Loaded: loaded (/usr/lib/systemd/system/named.service; enabled; vendor preset: disabled)
   Active: active (running) since Pzt 2019-02-04 10:43:37 UTC; 50min ago
  Process: 79284 ExecStop=/bin/sh -c /usr/sbin/rndc stop &gt; /dev/null 2&gt;&amp;1 || /bin/kill -TERM $MAINPID (code=exited, status=0/SUCCESS)
  Process: 79296 ExecStart=/usr/sbin/named -u named -c ${NAMEDCONF} $OPTIONS (code=exited, status=0/SUCCESS)
  Process: 79294 ExecStartPre=/bin/bash -c if [ ! &quot;$DISABLE_ZONE_CHECKING&quot; == &quot;yes&quot; ]; then /usr/sbin/named-checkconf -z &quot;$NAMEDCONF&quot;; else echo &quot;Checking of zone files is disabled&quot;; fi (code=exited, status=0/SUCCESS)
 Main PID: 79298 (named)
   CGroup: /system.slice/named.service
           └─79298 /usr/sbin/named -u named -c /etc/named.conf

Şub 04 10:43:37 ns2 named[79298]: zone 137.227.165.in-addr.arpa/IN: Transfer started.
Şub 04 10:43:37 ns2 named[79298]: transfer of '137.227.165.in-addr.arpa/IN' from 165.227.137.94#53: connected using 10.0.0.4#54200
Şub 04 10:43:37 ns2 named[79298]: zone 137.227.165.in-addr.arpa/IN: transferred serial 2019040100
Şub 04 10:43:37 ns2 named[79298]: transfer of '137.227.165.in-addr.arpa/IN' from 165.227.137.94#53: Transfer completed: 1 messages, 8...ytes/sec)
Şub 04 10:43:37 ns2 named[79298]: zone 137.227.165.in-addr.arpa/IN: sending notifies (serial 2019040100)
Şub 04 10:43:52 ns2 named[79298]: client 40.121.48.54#46157: received notify for zone 'emreberber.systems'
Şub 04 10:43:52 ns2 named[79298]: zone emreberber.systems/IN: refused notify from non-master: 40.121.48.54#46157
Şub 04 10:43:53 ns2 named[79298]: client 40.121.48.54#46157: received notify for zone '137.227.165.in-addr.arpa'
Şub 04 10:43:53 ns2 named[79298]: zone 137.227.165.in-addr.arpa/IN: refused notify from non-master: 40.121.48.54#46157
</code></pre>
<p>Son olarak Slave Sunucu üzerinde DNS sorgulaması yapabiliriz.</p><pre><code>$ dig emreberber.net @127.0.0.1
</code></pre>
<pre><code class="language-wiki">; &lt;&lt;&gt;&gt; DiG 9.9.4-RedHat-9.9.4-73.el7_6 &lt;&lt;&gt;&gt; emreberber.systems @127.0.0.1
;; global options: +cmd
;; Got answer:
;; -&gt;&gt;HEADER&lt;&lt;- opcode: QUERY, status: NOERROR, id: 58412
;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 3
;; WARNING: recursion requested but not available

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
;; QUESTION SECTION:
;emreberber.systems.		IN	A

;; ANSWER SECTION:
emreberber.systems.	604800	IN	A	35.234.125.178

;; AUTHORITY SECTION:
emreberber.systems.	604800	IN	NS	ns1.emreberber.systems.
emreberber.systems.	604800	IN	NS	ns2.emreberber.systems.

;; ADDITIONAL SECTION:
ns1.emreberber.systems.	604800	IN	A	165.227.137.94
ns2.emreberber.systems.	604800	IN	A	40.121.48.54

;; Query time: 0 msec
;; SERVER: 127.0.0.1#53(127.0.0.1)
;; WHEN: Sal Şub 05 07:59:24 UTC 2019
;; MSG SIZE  rcvd: 131
</code></pre>
<p>Yaptığımız tüm bu işlemlerin anlam kazanabilmesi için alan adı sağlayıcımızın panelinden Slave DNS sunucunun IP Adresini güncellememiz gerekir. İlginç bir şekilde tüm işlemler sorunsuz bir şekilde gerçekleşti ve böylece Google Cloud'da yer alan Slave Sunucunun fişini çekebilirim :)</p><p>Sonuç olarak özetlemek gerekirse,<br>Web Server --&gt; Google Cloud + Ubuntu<br>Master DNS Server --&gt; DigitalOcean + Ubuntu<br>Slave DNS Server --&gt; Microsoft Azure + CentOS</p><p>[1]<a href="https://emreberber.systems/digital-ocean-ve-google-cloud-ile-authoritative-only-bind-dns/"> Digital Ocean ve Google Cloud ile Authoritative Only Bind DNS</a><br>[2] <a href="https://devops.ionos.com/tutorials/configure-authoritative-name-server-using-bind-on-centos-7/">Configure Authoritative Name Server Using BIND On CentOS 7</a></p>
