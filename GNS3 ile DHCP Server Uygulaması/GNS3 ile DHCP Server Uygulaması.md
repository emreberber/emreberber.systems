 <p>Internete çıkan her cihazın bir IP Adresi vardır.DHCP Sunucu bu cihazların otomatik olarak IP Adresi almasında rol oynar.Bu blog yazımda mini bir DHCP Server uygulamasından bahsedeceğim.Yazının sonunda VirtualBox'daki DHCP Server ile GNS3 ortamındaki VPCS'lere IP Adresi ataması gerçekleştirmiş olacağız.</p><p><strong><strong>GNS3</strong></strong>(Graphical Network Simulator), ağ tasarımları yapmamızı sağlayan açık kaynak kodlu bir yazılımdır.Nasıl ki fiziksel olarak sunucu temin etmeyip VirtualBox'da sanal makine oluşturuyorsak, burada da network cihazlarını fiziksel olarak temin etmek yerine sanallaştırmış oluyoruz. </p><p><strong><strong>VPCS</strong></strong>, basit bilgisayar komutlarını çalıştırabileceğiniz bir bilgisayar simülasyon aracı. </p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture1-2.png" class="kg-image"></figure><p><strong><strong>Ubuntu 16.04 GNS3 Kurulumu</strong></strong> </p><p><code>sudo add-apt-repository ppa:gns3/ppa</code><br><code>sudo apt-get update</code><br><code>sudo apt-get install gns3-gui </code></p><p>VirtualBox'a Ubuntu Server kurulumunu anlatmaya zaten gerek yok.Sanal makinemiz default olarak sadece bir tane interface'e sahip olacaktır.Yapacağımız uygulama için iki adet interface gerekli.Yeni bir interface eklemek için sanal makinenin kapalı durumda olması gerekmekte.Ardından VirtualBox üzerinden sanal makinemizin ayarlarından Network sekmesine gelip <strong>Adapter 2 </strong>kısmında bulunan <strong>Enable Network Adapter</strong> kutucuğunu işaretliyoruz.Şuan için NAT olarak kalması sıkıntı yaratmaz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture2-1.png" class="kg-image"></figure><p>Ubuntu Server'ı ilk önce güncelleştirmeyi eksik etmiyoruz.Klaveyemizde numeric keypad mevcutsa büyük ihtimalle sanal makinede çalışmayacaktır.Güncelleştirmenin ardından bu sorun ortadan kalkar.</p><p><code>sudo apt update &amp;&amp; sudo apt upgrade </code></p><p>Birazdan sunucunun Internet ile olan bağlantısı son bulacağı için DHCP Server kurulumunu yapalım.</p><p><code>sudo apt-get install isc-dhcp-server</code><br><code>ifconfig </code></p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture3.png" class="kg-image"></figure><p>Az önce sanal makine ayarlarından ikinci interface'i eklememize rağmen burada gözükmeyecektir.Default olarak gelen enp0s3 interface'i gibi ikinci interface'in de bir ismi olmalı.Bunu öğrenmek için de,</p><p><code>ifconfig -a </code></p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture4-1.png" class="kg-image"></figure><p>Anlaşıldığı üzere eklediğimiz interface'in ismi enp0s8.DHCP Server'da bu interface'leri belirtelim.Konfigürasyon dosyalarında değişiklik yapmadan önce yedek almada fayda var.Ben dosyaların sonuna .old ekleyerek aynı dizine kopyalıyorum.Böylece herhangi bir problem oluştuğu anda o dosyayı tekrar eski haline geri getirebiliyorum.Sizin de bu veya buna benzer bi yöntem kullanmanızı tavsiye ederim.</p><p><code>sudo cp /etc/default/isc-dhcp-server /etc/default/isc-dhcp-server.old</code><br><code>sudo nano /etc/default/isc-dhcp-server</code> </p><pre><code class="language-wiki">INTERFACES=&quot;enp0s3 enp0s8&quot; 
</code></pre>
<p>olacak şekilde interface'lerimizi ekledik.</p><p><code>sudo nano /etc/network/interfaces </code></p><pre><code class="language-wiki"># This file describes the network interfaces available on your system 
# and how to activate them. For more information, see interfaces(5). 
source /etc/network/interfaces.d/* 
# The loopback network interface 
auto lo 
iface lo inet loopback 
# The primary network interface 
auto enp0s3 
iface enp0s3 inet dhcp 
</code></pre>
<p>Burada enp0s3 interface'inin IP Adresini DHCP'den aldığını görmekteyiz.Bize Static IP Adresi gerekli olduğu için  yazan yeri  ile yer değiştirip, DHCP'den gelen bilgileri de kendimiz tanımlamalıyız.Bu bilgiler ip, netmask, gateway ve broadcast'dir.Her iki interface için bu tanımlamaları yapalım.Burada ben enp0s3 için <strong><strong>192.168.10.1</strong></strong> ve enp0s8 için de <strong><strong>192.168.20.1</strong></strong> IP Adresini tercih ettim. </p><pre><code class="language-wiki"># This file describes the network interfaces available on your system 
# and how to activate them. For more information, see interfaces(5). 
source /etc/network/interfaces.d/* 
# The loopback network interface 
auto lo 
iface lo inet loopback 
# The primary network interface 
auto enp0s3 
iface enp0s3 inet static 
    address 192.168.10.1 
    netmask 255.255.255.0 
    gateway 192.168.10.1 
    broadcast 192.168.10.255 
# The secondary network interface 
auto enp0s8 
iface enp0s8 inet static 
    address 192.168.20.1 
    netmask 255.255.255.0 
    gateway 192.168.20.1 
    broadcast 192.168.20.255 
</code></pre>
<p>Interface'lerin yeni IP Adreslerini alabilmeleri için,</p><p><code>sudo service networking restart </code></p><p>Eğer hata alacak olursanız da :)</p><p><code>sudo reboot </code></p><p>diyerek yeni IP Adreslerimizi alabiliriz.</p><p><code>ifconfig </code></p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture5-1.png" class="kg-image"></figure><p>Görüldüğü üzere enp0s3 interface'ine 192.168.1.10, enp0s8 interface'ine de 192.168.20.1 IP Adresleri atanmış.Sıra DHCP Server ayarlarının yapılmasında.</p><h2 id="dhcp-server-yap-land-r-lmas-"><strong><strong>DHCP Server Yapılandırılması</strong></strong></h2><p>Az önce enp0s3 ve enp0s8 interface'lerini eklemiştik.</p><p><code>sudo nano /etc/dhcp/dhcpd.conf </code></p><p>Öncelikle domain name ile ilgili olan özellikleri yorum satırı haline getiriyoruz, bunlarla işimiz yok.Daha sonra  satırını da yorum satırı olmaktan kurtarıyoruz.</p><pre><code class="language-wiki"># option definitions common to all supported network... 
# option domain-name &quot;example.org&quot;; 
# option domain-name-servers ns1.example.org, ns2.example.org;  
default-lease-time 600; 
max-lease-time 7200; 
# If this DHCP server is the official DHCP server the local 
# network, the authoritative directive should be uncommented. 
authoritative; 
</code></pre>
<p>Yine aynı dosyadan devam ediyoruz.Bu kez işin en can alıcı kısmındayız.Burada interface'lerden çıkacak olan bilgileri belirliyoruz.Önce yorum satırlarını kaldırıp, enp0s8 için hemen altına bir blok daha ekliyoruz.</p><pre><code class="language-wiki"># A slightly different configuration for an internal subnet. 
# enp0s3 
subnet 192.168.10.0 netmask 255.255.255.0 { 
    range 192.168.10.2 192.168.10.254; 
    option subnet-mask 255.255.255.0 
    option routers 192.168.10.1; 
    option broadcast-address 192.168.10.255; 
    default-lease-time 600; 
    max-lease-time 7200; 
 } 
# enp0s8 
subnet 192.168.20.0 netmask 255.255.255.0 { 
    range 192.168.20.2 192.168.20.254; 
    option subnet-mask 255.255.255.0; 
    option routers 192.168.20.1; 
    option broadcast-address 192.168.20.255; 
    default-lease-time 600; 
    max-lease-time 7200; 
 } 
</code></pre>
<p>Burada subnet ile ilk satırda Network ID'leri yazdık.Blogun içinde range ile DHCP Sunucunun atayacağı IP Adres aralığını belirledik.X.X.X.1'li Adresleri router, X.X.X.255'li Adresleri de broadcast olarak ayarladığımız için aralığa dahil etmiyoruz.(Network ID ve Broadcast Adresleri bir makineye atanmaz)</p><h2 id="gns3"><strong><strong>GNS3</strong></strong></h2><p>Yazının başında kurmuş olduğumuz GNS3 programınında yeni proje oluşturuyoruz.</p><p>VirtualBox'da kurduğumuz DHCP Sunucuyu GNS3 projemize ekleyelim.Üst menüden Edit -&gt; Preferences -&gt; VirtualBox VMs adımlarını takip ettikten sonra New butonuna tıklıyoruz.Burada VM list kısmında VirtualBox'da oluşturduğumuz sanal makineler gözükür.DHCP Sunucuya hangi ismi verdiysek onu seçiyoruz.(DHCP)</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture6-1.png" class="kg-image"></figure><p>Finish dedikten sonra eklediğimiz sanal makineyi seçerek edit diyoruz.İlk olarak General Setting sekmesinde  kutucuğunu işaretli olacak şekilde seçiyoruz.Ardından Network sekmesinde ise sadece  kutucuğunu seçili olarak bırakıyoruz.Adapters sayısını da 2 olarak güncelliyoruz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture7-1.png" class="kg-image"></figure><p>Sol tarafta yer alan menülerde all devices sekmesinde eklediğimiz sanal makineyi görmemiz lazım.Sanal makinemizi şablonumuzun ortasına sürükle-bırak yönetimi ile ekliyoruz.Sanal makinenin alt ve üst kısmına ikişer tane VPCS ekliyoruz.DHCP Server ile VPCS'ler arasındaki bağlantı için de her bir interface'e bir adet ethernetswitch ekliyoruz.Kafanız karıştıysa, ki büyük ihtimalle, aşağıda son halini paylaştım.</p><p>Ardından bu makineleri birbirleri ile bağlantılı hale getirmeliyiz.Bunun için de yine sol tarafta yer alan  butonunu kullanıyoruz.Butona tıkladıktan sonra linklendirmeyi şu şekilde yaptım :</p><p>PC-1'in Ethernet0'ını Ethernetswitch-1'in Ethernet0'ına<br>PC-2'nin Ethernet0'ını Ethernetswitch-1'in Ethenet1'ine<br>DHCP-1'in Ethernet0'ını Ethernetswitch-1'in Ethernet7'sine</p><p>PC-3'ün Ethernet0'ını Ethernetswitch-2'nin Ethernet0'ına<br>PC-4'ün Ethenet0'ını Ethernetswitch-2'nin Ethernet1'ine<br>DHCP-1'in Ethernet1'ini Ethernetswitch-2'nin Ethernet7'sine</p><p>Burada PC'leri Ethernetswitch'lere 0'dan başlayarak, DHCP'yi Ethernetswitch'lere de 7'den düşerek bağladım.Bunun sebebi daha sonradan bağlantıların hangi cihazlar arasında olduğunu hatırlamak için kendimize yaptığımız bir işaret olarak düşünebiliriz.Teknik anlamda bir esprisi yok.</p><p>En son şöyle bir şey ortaya çıkmalı:</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture8-2.png" class="kg-image"></figure><p>Sanırım unuttuğumuz bir şey yok.Üstteki menüde yeşil play ikonu mevcut.Bu buton ile sistemi ayağa kaldıralım.Herhangi bir hata mesajıyla karşılaşmadıysak ne mutlu bize.Şimdi VPCS'lerin konsollarını açalım ve DHCP Sunucumuzdan IP Adresi talebinde bulunalım.VPCS-1'e sağ tıklayıp  dedikten sonra konsolumuz açılır.</p><p><code>dhcp</code> </p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture9-1.png" class="kg-image"></figure><p>IP Adresi alırken dikkatinizi çeken bir kısım olmuştur."DORA"</p><p><strong><strong>DORA Nedir ?</strong></strong> </p><p>DHCP’den IP Adresi alma işlemi 4 aşamada gerçekleşir.Viki'de "DHCP’nin Çalışma Prensipleri" başlığı altında gayet iyi anlatılmış linkini <a href="http://www.wiki-zero.co/index.php?q=aHR0cHM6Ly90ci53aWtpcGVkaWEub3JnL3dpa2kvREhDUA">buraya</a> bırakıyorum. </p><p>Diğer makineler için de IP Adresi alalım.Makinelere atanan IP Adreslerini öğrenmek için de,</p><p><code>show ip </code></p><p>komutunu kullanıyoruz.Ayrıca GNS3 programını kapattığımız zaman atanan IP Adresleri kaydedilmeyecektir.Bu yüzden</p><p><code>save</code> </p><p>komutu ile yaptığımız bu işlemleri kaydediyoruz.Böylece projeyi her açtığımızda sunucudan IP Adresi talep etmemize gerek kalmayacaktır.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture10-1.png" class="kg-image"></figure><p>Ayrıca sunucumuzda</p><p><code>sudo service isc-dhcp-server status </code></p><p>komutu ile dhcp servisimizin durumunu kontrol edebiliriz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture11-1.png" class="kg-image"></figure><p>GNS3 kurulumu sırasında  programı da yükleniyor.VPCS'lerden herhangi birinin link bağlantısına sağ tıklayıp  dedikten sonra Wireshark programı açılır.VPCS'in konsolundan IP Adresi talebinde bulunduğumuzda, gerçekleşen işlemleri Wireshark'da görebiliriz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture12-1.png" class="kg-image"></figure><p>Yazı fazla uzamasın diye subnet konusuna fazla değinmedim.Başka bir blog yazısında hem subnet işlemini teorik olarak anlatıp ardından GNS3'de simule edilmesini yazarım.Şimdilik bu kadar ;)</p><p>[1] <a href="http://www.wiki-zero.co/index.php?q=aHR0cHM6Ly90ci53aWtpcGVkaWEub3JnL3dpa2kvREhDUA">DHCP</a><br>[2] <a href="https://www.tecmint.com/install-dhcp-server-in-ubuntu-debian/">How to Install a DHCP Server in Ubuntu and Debian</a> </p>


// 07 September 2018  GNS3, DHCP, Ubuntu Server
