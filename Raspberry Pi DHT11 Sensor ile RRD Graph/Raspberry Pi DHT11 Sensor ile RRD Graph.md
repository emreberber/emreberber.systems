<p> Stajda yaklaşık bir hafta boyunca uğraştığım bir projeyi blog yazısına dökmek istedim.Bu projede Raspberry Pi 3 ile DHT11 - Sıcaklık ve Nem Sensörünü kullanıp veriyi RRD grafiği ile göstereceğiz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture13.png" class="kg-image"></figure><p>Proje için belirlenen dilin  olması ve benim python bilgimin bu proje için yeterli olmamasından ötürü önceden yapılmış proje arayaşına girdim.RRD grafiği çizdiren bir proje buldum fakat projede kullanılan sensör DHT22 idi.Ayrıca elimdeki Raspberry Pi'de GrovePi adı verilen bir kit bulunuyordu ve DHT11 sensörü bu kite bağlıydı.Yani veriyi projedekinden farklı bir yolla çekmemiz gerekecekti.Bahsettiğim proje linkine <a href="https://github.com/bylexus/dht22_reader"><strong><strong>buradan</strong></strong></a>ulaşabilirsiniz.Ya tutarsa, diyerek başladığım projeyi sonunda istediğim hale getirebildim. </p><p>Projede web tarafı nodejs üzerinde koşmakta.Ben sadece local'de RRD grafiklerini göstermeyi anlatacağım bu yüzden bütün dosyaları kullanmamıza gerek kalmayacak.Dosya yapısı ise şöyle olacak,</p><pre><code class="language-wiki">index.html 
    reader.ini 
    reader.py 
    create_graphs.py 
    /data 
        ... 
    /output 
        ... 
    </code></pre>
    <p>reader.py çalıştığı zaman data dizini içerisine .rrd uzantılı veritabanını oluşturacaktır.Ardından her çalışmasında bu veritabanının üzerine kaydedecektir.create_graphs.py çalıştığında ise veritabanından aldığı verileri farklı zaman aralıkları olacak şekilde 7 adet png çıktıyı output dizininde depolayacaktır.Dosyanın her çalıştığı anda yeni resim oluşturmak yerine üstüne yazması bizim işimize geliyor.Hem eski resimler depolanmamış oluyor hem de resimlerin isimleri değişmemiş oluyor.</p><p>Yukarıda "her çalışmasında" ve "üstüne yazma" gibi ifadeler kullandım.Bunun sebebi her iki python dosyasını zamanlanmış görev olarak dakikada bir çalışacak olmasıdır.Github Reposunda 5 dakikada bir olacak şekilde yazmış fakat sıcaklık ve nem değerleri için 5 dakika bana fazla geldiğinden 1 dakika olarak ayarladım.</p><p>GrovePi modülünü yüklemek için,<br><code>sudo curl -kL dexterindustries.com/update_grovepi | bash</code><br><code>sudo pip install grovepi</code><br><code>sudo reboot</code> </p><p>Bu modülü yüklememizin tek sebebi var.Sensörden veriyi bu modül yardımıyla çekmek.Terminal ekranımızda veri test işlemi gerçekleştirelim.</p><p><code>python</code></p><pre><code class="language-python">import grovepi 
    temperature, humidity = grovepi.dht(2, 0) 
    print(temperature) 
    print (humidity) 
    quit() 
    </code></pre>
    <p>grovepi.dht(2, 0)'da <strong><strong>2</strong></strong> ile kullandığımız , grovepi modülünde  girişine bağladığımız için 2, <strong><strong>0</strong></strong> da  sensörü kullanıldığını belirtiyor.(DHT22 kullanmış olsaydık 0 yerine 1 yazmamız gerekecekti.) </p><p><strong><strong>reader.ini</strong></strong> dosyasında sadece <strong><strong>set_name</strong></strong>'i Room olarak değiştirdim.Onun dışında herhangi bir değişiklik yapmadım. </p><pre><code class="language-textile">[system] 
    log_level: DEBUG 
    output_dir: output 
    data_dir: data 
    [dataprovider] 
    provider: dht22 
    set_name: Room 
    gpio: 4 
    measure_interval: 300 
    [graph] 
    width: 600 
    height: 250 
    lower_limit: 0 
    enable_combined: 1 
    enable_temp_graph: 0 
    enable_humidity_graph: 0 
    title_temperature: Temperature of $set_name 
    title_humidity: Humidity of $set_name 
    title: Temperature &amp; Humidity of $set_name 
    </code></pre>
    <p>Proje DHT22 Sensörüne göre yazıldığı için isimlendirmeler de buna göre yapılmış.Çok da önemli olmadığından dolayı isimlendirmelerde değişiklik yapmadım.</p><p>İlk önce reader.py dosyasında grovepi  modulünü import ediyoruz</p><pre><code class="language-python">import grovepi 
    </code></pre>
    <p>Daha sonra DHT22DataProvider sınıfında yer alan <strong><strong>readData</strong></strong> metodunda ufak bir değişikliğe gidiyoruz. </p><pre><code class="language-python">def readData(self): 
            humidity = None 
            temperature = None 
            while humidity is None or temperature is None: 
                temperature, humidity = grovepi.dht(2, 0) 
            humidity = round(humidity) 
            temperature = round(temperature, 1) 
            return {'temperature':temperature, 'humidity': humidity} 
    </code></pre>
    <p>create_graphs.py dosyasında ise herhangi bir değişiklik yapmamıza gerek yok.Sıra geldi bu iki python dosyasını her dakikada çalışacak şekilde ayarlamaya.</p><p><code>crontab -e </code></p><pre><code class="language-wiki"># Edit this file to introduce tasks to be run by cron. 
    # 
    # Each task to run has to be defined through a single line 
    # indicating with different fields when the task will be run 
    # and what command to run for the task 
    # 
    # To define the time you can provide concrete values for 
    # minute (m), hour (h), day of month (dom), month (mon), 
    # and day of week (dow) or use '*' in these fields (for 'any').# 
    # Notice that tasks will be started based on the cron's system 
    # daemon's notion of time and timezones. 
    # 
    # Output of the crontab jobs (including errors) is sent through 
    # email to the user the crontab file belongs to (unless redirected). 
    # 
    # For example, you can run a backup of all your user accounts 
    # at 5 a.m every week with: 
    # 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/ 
    # 
    # For more information see the manual pages of crontab(5) and cron(8) 
    # 
    # m h  dom mon dow   command 
    MAILTO=&quot;&quot; 
    */1 *   *   *   *    /usr/bin/env python /home/pi/dht22_reader/reader.py 
    */1 *   *   *   *    /usr/bin/env python /home/pi/dht22_reader/create_graphs.py 
    </code></pre>
    <p>MAILTO="" eklememin sebebi, görevleri belirttikten sonra sistemin kendine bilgilendirme maili göndermesidir.İsterseniz bu satırı eklemeyerek bunu nasıl farkettiğimi anlayabilirsiniz :)</p><p>reader.py çalıştığında data dizininde <strong><strong>Room.rrd</strong></strong> dosyasının oluştuğunu görebilirsiniz.Room ismini reader.ini dosyasındaki set_name'den almaktadır. </p><p>As projedeki grafiğin görüntülendiği sayfayı beğenmediğimden dolayı kendim bi <strong><strong>index.html</strong></strong> hazırladım.Onu da buraya bırakayım. </p><pre><code class="language-wiki">&lt;!doctype html&gt; 
    &lt;html&gt; 
    &lt;head&gt; 
        &lt;title&gt;DHT Sensor Data&lt;/title&gt; 
        &lt;meta http-equiv=&quot;Content-Type&quot; content=&quot;text/html; charset=UTF-8&quot; /&gt; 
        &lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1&quot;&gt; 
        &lt;link rel=&quot;stylesheet&quot; href=&quot;https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css&quot;&gt; 
        &lt;style&gt; 
            body { 
                text-align: center; 
                background: #FAFAFA; 
                overflow-x: hidden; 
            }        
        &lt;/style&gt; 
    &lt;/head&gt; 
    &lt;body&gt; 
        &lt;h1&gt;DHT Sensor Data &lt;button type=&quot;button&quot; class=&quot;btn btn-sm btn-success&quot; disabled&gt;RRD&lt;/button&gt;&lt;/h1&gt; 
          &lt;div class=&quot;form-group row justify-content-center&quot;&gt;        
            &lt;div class=&quot;col-sm-2&quot;&gt; 
                &lt;select class=&quot;form-control&quot; onchange=&quot;document.getElementById('rrd_graph').src=timeInterval[this.value];&quot;&gt; 
                  &lt;option value=&quot;12h&quot;&gt;12 hours&lt;/option&gt; 
                  &lt;option value=&quot;24h&quot;&gt;24 hours&lt;/option&gt; 
                  &lt;option value=&quot;5d&quot;&gt;5 days&lt;/option&gt; 
                  &lt;option value=&quot;7d&quot;&gt;7 days&lt;/option&gt; 
                  &lt;option value=&quot;1m&quot;&gt;1 months&lt;/option&gt; 
                  &lt;option value=&quot;6m&quot;&gt;6 months&lt;/option&gt; 
                  &lt;option value=&quot;1y&quot;&gt;1 years&lt;/option&gt; 
                &lt;/select&gt; 
            &lt;/div&gt; 
            &lt;a href=&quot;&quot; class=&quot;btn btn-danger&quot;&gt;Refresh !&lt;/a&gt; 
          &lt;/div&gt; 
        &lt;img src=&quot;output/Room_combined_12_hours.png&quot; alt=&quot;RRD_Graph&quot; id=&quot;rrd_graph&quot;&gt; 
        &lt;script&gt; 
            var timeInterval = { 
                &quot;12h&quot; : &quot;output/Room_combined_12_hours.png&quot;, 
                &quot;24h&quot; : &quot;output/Room_combined_24_hours.png&quot;, 
                &quot;5d&quot; : &quot;output/Room_combined_5_days.png&quot;, 
                &quot;7d&quot; : &quot;output/Room_combined_7_days.png&quot;, 
                &quot;1m&quot; : &quot;output/Room_combined_1_months.png&quot;, 
                &quot;6m&quot; : &quot;output/Room_combined_6_months.png&quot;, 
                &quot;1y&quot; : &quot;output/Room_combined_1_years.png&quot;            
            }; 
        &lt;/script&gt;  
    &lt;/body&gt; 
    &lt;/html&gt; 
    </code></pre>
    <p>index.html dosyasını tarayıcıda açtığımızda,</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture14.png" class="kg-image"></figure><p>Projenin en önemli kısmı grafikleri elde etmekti.Web sunucusunda bu grafikleri görüntülemek için tek yapmamız gereken image dosyalarını yine zamanlanmış görev olarak dakikada bir sunucuya göndermektir.Bunun için <strong>scp</strong> komutunu araştırabilirsiniz.</p><figure class="kg-card kg-image-card"><img src="/content/images/2018/10/Picture15.png" class="kg-image"></figure><p>[1] <a href="https://alexi.ch/projects/dht22-sensor-on-raspberry-pi/">DHT22 sensor on Raspberry Pi</a><br>[2] <a href="https://github.com/DexterInd/GrovePi/blob/master/Software/Python/grove_temperature_sensor.py">DexterInd - GrovePi</a> </p>

    
    // 23 September 2018  Raspberry Pi, DHT11, RRD, Python
