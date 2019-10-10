<p>Bu yazımda blogumu <a href="https://www.digitalocean.com/"><strong><strong>Digital</strong> <strong>Ocean</strong></strong></a> ve <a href="https://cloud.google.com/"><strong><strong>Google</strong> <strong>Cloud</strong></strong></a> üzerinde oluşturduğum <strong><strong>nameserver</strong></strong>'lar ile nasıl yayınladığımı anlatacağım. </p><p><strong><strong>DNS</strong></strong> olarak <strong><strong>BIND</strong></strong> ve <strong><strong>Authoritative-Only</strong></strong> olacak şekilde kurdum.BIND'ı tercih etme sebebim günümüzde popüler olması ve kolay config edilebilmesi.Ayrıca authoritative-only ile sadece yetkili olduğu domainler üzerindeki isteklere cevap vermesini sağlıyoruz.Böylece sunucumuz daha performanslı çalışmış olacak. </p><p>Google Cloud'ın bir yıl geçerli <strong><strong>300$</strong></strong>, <a href="https://education.github.com/pack"><strong><strong>Github Education</strong></strong></a>'ının da Digital Ocean için <strong><strong>50$</strong></strong> kredi verdiğini hatırlatmış olalım.Digital Ocean'da master server, Google Cloud'da iki ayrı makine oluşturup birinde slave server diğerinde de websitemi barındırmayı tercih ettim.Benim için güzel bir tecrübe oldu.Ayrıca blogumu <a href="https://ghost.org/"><strong><strong>Ghost</strong></strong></a> ile yayına aldım.Bu süreci de bir blog yazısında yazmayı düşünüyorum. </p><p>Master ayarlarında, slave ve web sunucularının IP Adresleri gerekli olduğu için ilk önce bu IP Adreslerini elde edelim.<br>Google Cloud'da Compute Engine -&gt; Sanal Makine Örnekleri -&gt; Örnek oluştur adımlarını takip ediyoruz.Slave için ns2 ismini kullandım.Dağıtımı <strong><strong>Ubuntu Server 16.04</strong></strong> olarak seçtim ve makine türünü 1 paylaşımlı vCPU - 0.6 GB Memory olacak şekilde belirledim.En son HTTP ve HTTPS trafiğine izin ver alanlarını check yaptım.Bu sunucuya <strong><strong>ns2</strong></strong>, Web sunucu için de <strong><strong>www</strong></strong> ismini verdim ve bölge hariç aynı özellikleri uyguladım.Bölgeyi Slave sunucunun bölgesinden farklı seçmemiz gerekiyor.Bunun sebebi birazdan IP Adreslerini static olarak belirleyecek olmamız.Google Cloud bize aynı bölgeden yalnızda bir tane Static IP vermekte. </p><p>Digital Ocean default olarak Static IP atadığından dolayı sadece Google Cloud için Static IP atamasını gerçekleştireceğiz.Static IP adresleri belirlemek için de ana menüden VPC Ağı -&gt; Harici IP Adresleri admlarını izliyoruz.Burada tür olarak gösterilen yerleri static olarak değişirip isim veriyoruz.İsimleri makinemizle aynı olacak şekilde verirsek daha sonra hangi makineye ait olduğunu hatırlamakta zorluk çekmeyiz.Static IP Adresi atamasının sebebine gelecek olursak, DNS kurulumunda Master, Slave ve Web sunucuların IP Adreslerini konfigurasyon dosyalarında kullanacak olmamızdır.IP Adreslerimiz değiştiğinde yaptığımız ayarlar geçerli olamayacak ve her defasında bu dosyalarda değişiklik yapmamız gerekecekti.Oysaki DNS sistemimiz 7/24 up olacak şekilde çalışmalıdır.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture8.png" class="kg-image"></figure><h1 id="master-bind-server"><strong><strong>Master Bind Server</strong></strong></h1><p><a href="http://cloud.digitalocean.com/">cloud.digitalocean.com</a> adresinde <strong>Droplets</strong> sekmesinde Create butonu ile master nameserver'ımızı oluşturacağız.Distribution olarak Ubuntu 16.04 , Choose size tarafında ise 1GB Ram - 25GB SSD  kullandım.Datacenter'ı Franfurt seçtim (bağlantıda sıkıntı çekmemek için yakın bölgelerden tercihimi yaptım).Hostname'i ns1 belirledim.Ardından Create butonu ile onay verdim.Ayrıca  bağlantısı yapmak için Networking sayfasında Firewalls sekmesinden Inbound Rules başlığı altında type olarak ssh oluşturabiliriz.Sunucumuzun kullanıcı adı root iken parolayı default olarak vermekte.Access sekmesinden, mail adresimize default parolayı gönderebiliyoruz.Makineyi ilk açışımızda da parolamızı değiştirebiliyoruz. </p><p>Şimdi sistemimizi yavaştan kurmanın zamanı geldi.Makinelerimizin IP Adreslerini bir kenara not alalım.</p><p>· Master <strong><strong>165.227.137.94</strong></strong> </p><p>· Slave <strong><strong>35.189.110.151</strong></strong> </p><p>· Web <strong><strong>35.204.225.40</strong></strong> </p><p>Master ve Slave sunucularımızın her ikisinde de yapmamız gereken bir detay var.Bind sunucumuzu IPv4 moduna setlemeliyiz.</p><p><code>sudo nano /etc/systemd/system/bind9.service </code></p><pre><code class="language-wiki">[Service] 
ExecStart=/usr/sbin/named -f -u bind -4 
</code></pre>
<figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture9.png" class="kg-image"></figure><p>Sistemin ilk açılışında gelenektir, update yapalım.Ardından Bind kurulumunu gerçekleştirelim.</p><p><code>sudo apt-get update &amp;&amp; apt-get upgrade</code><br><code>sudo apt-get install bind9 bind9utils bind9-doc</code><br><code>sudo nano /etc/bind/named.conf.options</code> </p><pre><code class="language-wiki">options { 
        directory &quot;/var/cache/bind&quot;; 
        recursion no; 
        allow-transfer { none; }; 
        dnssec-validation auto; 
        auth-nxdomain no;    # conform to RFC1035 
        listen-on-v6 { any; }; 
}; 
</code></pre>
<p>recursion no; ve allow-transfer { none; };  satırlarını ekledikten sonra kaydedip çıkıyoruz.Burada rekürsif sorgulamayı kapatarak diğer DNS sunucular ile haberleşmemesini sağlıyoruz.allow-transfer ile de dışarıdan gelebilecek zone transfer isteklerini engellemiş oluyoruz. </p><p><code>sudo nano /etc/bind/named.conf.local </code></p><pre><code class="language-wiki">zone &quot;emreberber.net&quot; { 
        type master; 
        file &quot;/etc/bind/zones/db.emreberber.net&quot;; 
        allow-transfer { 35.189.110.151; }; // Slave IP 
}; 
zone &quot;137.227.165.in-addr.arpa&quot; { 
        type master; 
        file &quot;/etc/bind/zones/db.165.227.137&quot;; 
        allow-transfer { 35.189.110.151; }; // Slave IP 
}; 
</code></pre>
<p>Burada Master'da bulunan zone dosyalarının konumlarını ve zone transferi için izin verdiğimiz Slave sunucusunun IP Adresini ekledik.(emreberber.systems'a daha sonradan geçtim.)</p><p><code>sudo mkdir /etc/bind/zones</code><br><code>sudo cp /etc/bind/db.local /etc/bind/zones/db.emreberber.net</code><br><code>sudo cp /etc/bind/db.127 /etc/bind/zones/db.165.227.137</code> </p><p><code>sudo nano /etc/bind/zones/db.emreberber.net </code></p><pre><code class="language-wiki">; 
; BIND data file for local loopback interface 
; 
$TTL    604800 
@       IN      SOA     ns1.emreberber.net. admin.emre.ninja. ( 
                     2018080400         ; Serial 
                          28800         ; Refresh 
                           7200         ; Retry 
                         604800         ; Expire 
                            600 )       ; Negative Cache TTL 
; 
; Name servers 
emreberber.net. IN      NS      ns1.emreberber.net. 
emreberber.net. IN      NS      ns2.emreberber.net. 
; A records for name servers 
ns1             IN      A       165.227.137.94 
ns2             IN      A       35.189.110.151 
; Other A records 
@               IN      A       35.204.225.40 
www             IN      CNAME   @ 
</code></pre>
<p>Serial tanımlarken <strong>YYYYMMDDnn</strong>  formatını kullanıyoruz.Burada nn değeri <strong><strong>0</strong></strong>'dan başlayıp, her değişiklikte <strong><strong>1 </strong></strong>arttırmamız gerekmekte.Ayrıca değişiklik yapılan her gün için de xx değerimiz <strong><strong>sıfırlanmaktadır</strong></strong>. </p><p><strong><strong>Reverse Zone Dosyasının Oluşturulması</strong></strong><br> IP Adresinden domain name bulunması için reverse zone dosyalarına ihtiyaç duyarız. </p><p><code>sudo nano /etc/bind/zones/db.165.227.137 </code></p><pre><code class="language-wiki">; 
; BIND reverse data file for local loopback interface 
; 
$TTL    600 
@       IN      SOA     emreberber.net. admin.emreberber.net. ( 
                     2018080101         ; Serial 
                          28800         ; Refresh 
                           7200         ; Retry 
                         604800         ; Expire 
                            600 )       ; Negative Cache TTL 
; 
; Name servers 
        IN      NS      ns1.emreberber.net. 
        IN      NS      ns2.emreberber.net. 
; PTR records 
94      IN      PTR     ns1.emreberber.net. 
151     IN      PTR     ns2.emreberber.net. 
40      IN      PTR     www.emreberber.net.
</code></pre>
<p> <strong><strong>Dosyaların Test Edilmesi</strong></strong><br> Oluşturduğumuz dosyalarda herhangi bir yazım hatası olup olmadığını kontrol ediyoruz. </p><p><code>sudo named-checkconf</code><br> <code>sudo named-checkzone emreberber.net /etc/bind/zones/db.emreberber.net</code><br> zone emreberber.net/IN: loaded serial <strong><strong>2018080400</strong></strong><br> OK<br> <code>sudo named-checkzone 137.227.165.in-addr.arpa /etc/bind/zones/db.165.227.137 </code></p><p><strong><strong>Bind Server Çalıştırılması</strong></strong><br><code> sudo service bind9 start</code><br><code> sudo service bind9 status </code></p><pre><code class="language-wiki">● bind9.service - BIND Domain Name Server 
   Loaded: loaded (/etc/systemd/system/bind9.service; enabled; vendor preset: enabled) 
  Drop-In: /run/systemd/generator/bind9.service.d 
           └─50-insserv.conf-$named.conf 
   Active: active (running) since Sat 2018-08-04 10:38:10 UTC; 3s ago 
     Docs: man:named(8) 
  Process: 12559 ExecStop=/usr/sbin/rndc stop (code=exited, status=0/SUCCESS) 
 Main PID: 12567 (named) 
    Tasks: 4 
   Memory: 10.2M 
      CPU: 24ms 
   CGroup: /system.slice/bind9.service 
           └─12567 /usr/sbin/named -f -u bind -4 
Aug 04 10:38:10 ns1 named[12567]: zone 0.in-addr.arpa/IN: loaded serial 1 
Aug 04 10:38:10 ns1 named[12567]: zone 127.in-addr.arpa/IN: loaded serial 1 
Aug 04 10:38:10 ns1 named[12567]: zone emreberber.net/IN: loaded serial 2018080400 
Aug 04 10:38:10 ns1 named[12567]: zone 137.227.165.in-addr.arpa/IN: loaded serial 2018080101 
Aug 04 10:38:10 ns1 named[12567]: zone 255.in-addr.arpa/IN: loaded serial 1 
Aug 04 10:38:10 ns1 named[12567]: zone localhost/IN: loaded serial 2 
Aug 04 10:38:10 ns1 named[12567]: all zones loaded 
Aug 04 10:38:10 ns1 named[12567]: running 
Aug 04 10:38:10 ns1 named[12567]: zone emreberber.net/IN: sending notifies (serial 2018080400) 
Aug 04 10:38:10 ns1 named[12567]: zone 137.227.165.in-addr.arpa/IN: sending notifies (serial 2018080101) 
</code></pre>
<p>Log kayıtlarına bakmak için ise,<br><code>sudo tail -f /var/log/syslog </code></p><h1 id="slave-bind-server"><strong><strong>Slave Bind Server</strong></strong></h1><p>Slave tarafında sadece named.conf.options ve named.conf.local dosyalarında değişiklik yapıyoruz.Master'da yaptığımız gibi  ve  satırlarını ekliyoruz.<br><br><code>sudo nano /etc/bind/named.conf.options</code> </p><pre><code class="language-wiki">options { 
        directory &quot;/var/cache/bind&quot;; 
        recursion no; 
        allow-transfer { none; }; 
        dnssec-validation auto; 
        auth-nxdomain no;    # conform to RFC1035 
        listen-on-v6 { any; }; 
}; 
</code></pre>
<p>named.conf.options dosyasında da Master'ın IP Adresi ve zone dosyalarının konumlarını belirliyoruz.<br><br><code>sudo nano /etc/bind/named.conf.options</code> </p><pre><code class="language-textfile">zone &quot;emreberber.net&quot; { 
        type slave; 
        file &quot;db.emreberber.net&quot;; 
        masters { 165.227.137.94; };  // Master IP 
}; 
zone &quot;137.227.165.in-addr.arpa&quot; { 
        type slave; 
        file &quot;db.165.227.137&quot;; 
        masters { 165.227.137.94; };  // Master IP 
}; 
</code></pre>
<p>Slave için yapmamız gereken ayarlar bu kadar.Kontrol adımlarını Slave için de yaptıktan sonra sunucumuzu başlatabiliriz.</p><p><code>sudo named-checkconf</code><br><code>sudo service bind9 start</code><br><code>sudo service bind9 status</code> </p><pre><code class="language-wiki">● bind9.service - BIND Domain Name Server 
   Loaded: loaded (/etc/systemd/system/bind9.service; enabled; vendor preset: enabled) 
  Drop-In: /run/systemd/generator/bind9.service.d 
           └─50-insserv.conf-$named.conf 
   Active: active (running) since Mon 2018-08-06 06:39:10 UTC; 1s ago 
     Docs: man:named(8) 
  Process: 8844 ExecStop=/usr/sbin/rndc stop (code=exited, status=0/SUCCESS) 
 Main PID: 8848 (named) 
    Tasks: 4 
   Memory: 10.1M 
      CPU: 34ms 
   CGroup: /system.slice/bind9.service 
           └─8848 /usr/sbin/named -f -u bind -4 
Aug 06 06:39:10 ns2 named[8848]: zone 255.in-addr.arpa/IN: loaded serial 1 
Aug 06 06:39:10 ns2 named[8848]: zone localhost/IN: loaded serial 2 
Aug 06 06:39:10 ns2 named[8848]: all zones loaded 
Aug 06 06:39:10 ns2 named[8848]: running 
Aug 06 06:39:10 ns2 named[8848]: zone emreberber.net/IN: sending notifies (serial 2018080400) 
Aug 06 06:39:10 ns2 named[8848]: zone 137.227.165.in-addr.arpa/IN: sending notifies (serial 2018080101) 
Aug 06 06:39:10 ns2 named[8848]: client 35.189.110.151#59435: received notify for zone 'emreberber.net' 
Aug 06 06:39:10 ns2 named[8848]: zone emreberber.net/IN: refused notify from non-master: 35.189.110.151#59435 
Aug 06 06:39:11 ns2 named[8848]: client 35.189.110.151#43881: received notify for zone '137.227.165.in-addr.arpa' 
Aug 06 06:39:11 ns2 named[8848]: zone 137.227.165.in-addr.arpa/IN: refused notify from non-master: 35.189.110.151# 
</code></pre>
<p>Burada önemli olan nokta, zone dosyalarında belirlediğimiz serial'ler ile buradaki serial'lerin aynı olması ve serial değiştiğinde de burada güncel serial'i görebilmemizdir.</p><p><code>sudo tail -f /var/log/syslog </code></p><p>Son olarak, yaptıklarımızın anlam kazanması için domain sağlayıcının panelinden domainimize ait olan nameserver bilgilerini kendi nameserver'larmız ile değiştirilmesi kaldı.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture10.png" class="kg-image"></figure><p>DNS sisteminin doğru çalışıp çalışmadığını test etme zamanı geldi.<strong><strong>dig</strong></strong> komutu ile kendi sunucumuza dns sorgusu yapıyoruz.<br><code>dig emreberber.net @127.0.0.1 </code></p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture11.png" class="kg-image"></figure><p>ANSWER SECTION tarafında web sunucmuzun ip adresini gösteren A kaydının dönmesi, doğru işler yaptığımızı gösterir.<br>Bir başka test yönetimi için <a href="http://intodns.com/">intodns.com</a> 'a başvurabiliriz.Burada kayıtlarımızın ne ölçüde doğru ayarlandığını görmekteyiz.Hata ve uyarı mesajlarına göre gerekli düzenlemeleri yapmakta fayda var. </p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture12.png" class="kg-image"></figure><p>Bir başka blog yazısında Ghost kurulumu ve editlenmesi, <a href="https://letsencrypt.org/">Let's Encrypt</a> ile SSL, <a href="https://disqus.com/">Disqus</a> gibi konulara değinmek gibi bir niyetim var.Ayrıca DNS üzerine başka blog yazıları da yazacağım. </p><p>[1] <a href="http://www.zytrax.com/books/dns/">Zytrax - Pro DNS and BIND</a><br>[2] <a href="https://www.digitalocean.com/community/tutorials/how-to-configure-bind-as-an-authoritative-only-dns-server-on-ubuntu-14-04">How To Configure Bind as an Authoritative-Only DNS Server on Ubuntu 14.04</a> </p>


// 25 August 2018  Google Cloud, Digital Ocean, Bind, DNS
