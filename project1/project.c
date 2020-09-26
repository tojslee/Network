#include <stdio.h>
#include <pcap.h>
char errbuf[PCAP_ERRBUF_SIZE];
pcap_if_t *allDevs;
int network; // network variable
int sniff; // sniff type variable 1:HTTP 2:DNS
int no = 1;
int twoOffset = 0;

void parsing(u_char *param, const struct pcap_pkthdr *header, const u_char *pkt_data);

int main(){

    // selection of networks
    if(pcap_findalldevs(&allDevs, errbuf) < 0){
        printf("pcap_findalldevs error\n");
        printf("%s\n", errbuf);
        return 0;
    }

    if(!allDevs){
        printf("%s\n", errbuf);
    }

    int counter = 0;
    for(pcap_if_t *i = allDevs;i;i = i->next){
        printf("%d: %s", ++counter, i->name);
        if(i->description){printf(" (%s)", i->description);}
        printf("\n");
    }
    printf("Select Network: ");
    scanf("%d", &network);
    while(network <= 0 || network > counter){
        printf("Select Network: ");
        scanf("%d", &network);
    }

    // choose whether to sniff
    printf("Choose whether to sniff.(1:HTTP, 2:DNS): ");
    scanf("%d", &sniff);
    while(sniff <= 0 || sniff > 2){
        printf("Choose whether to sniff.(1:HTTP, 2:DNS): ");
        scanf("%d", &sniff);
    }

    // opening device for sniffing
    pcap_if_t *dev = allDevs;
    for(int i=0;i<network-1;i++){
        dev = dev->next;
    }
    //printf("%s\n", dev->name);
    if(strcmp(dev->name, "any") == 0){
        twoOffset = 1;
    }

    pcap_t *handle;
    handle = pcap_open_live(dev->name, BUFSIZ, 1, 1000, errbuf);
    if(handle == NULL){
        printf("Cannot open device %s : %s\n", dev->name, errbuf);
        pcap_freealldevs(allDevs);
        return 0;
    }

    //pcal_loop(handle, 0, parsing, NULL);
//
    char *FILTER_RULE;
    if(sniff == 1){
        FILTER_RULE = "port 80";
    }
    else if (sniff == 2){
        FILTER_RULE = "port 53";
    }
    struct bpf_program fcode;
    //printf("1\n");
    if(pcap_compile(handle, &fcode, FILTER_RULE, 1, NULL) < 0){
        printf("pcap compile failed\n");
        pcap_freealldevs(allDevs);
        return 0;
    }

    //printf("2\n");
    if(pcap_setfilter(handle, &fcode) < 0){
        printf("pcap compile failed\n");
        pcap_freealldevs(allDevs);
        return 0;
    }

    pcap_freealldevs(allDevs);
    //printf("3\n");
    pcap_loop(handle, 0, parsing, NULL);
    //printf("4\n");

    pcap_close(handle);
    return 0;
}

void parsing(u_char *param, const struct pcap_pkthdr *header, const u_char *pkt_data){
    // pcap_pkthdr *header -> packet information
    /* struct pcap_pkthdr{
        struct timeval ts; pack capture time
        bpf_u_int32 caplen; capture packet length
        bpf_u_int32 len; real packet length
    }
*/  
    int offsetNum;
    if(twoOffset){
        offsetNum = 2;
    }
    else{offsetNum = 0;}

    // u_char *pkt_data -> packet start address
    if(sniff == 1){ // if packet of HTTP
        int flag = 0;
        
        //printf("%c%c%c%c\n", *(pkt_data + 0x36 + offsetNum), *(pkt_data + 0x37 + offsetNum),
        // *(pkt_data + 0x38 + offsetNum), *(pkt_data + 0x39 + offsetNum));
        if(*(pkt_data + 0x36 + offsetNum) == 0x47){ // GET
            if(*(pkt_data + 0x37+ offsetNum) == 0x45 && *(pkt_data + 0x38+ offsetNum) == 0x54){
                flag = 1;
            }
        }
        else if(*(pkt_data + 0x36+ offsetNum) == 0x50 && *(pkt_data + 0x37+ offsetNum) == 0x4F && \
        *(pkt_data + 0x38+ offsetNum) == 0x53 && *(pkt_data + 0x39+ offsetNum) == 0x54){ // POST
            flag = 1;
        }
        else if(*(pkt_data + 0x36+ offsetNum) == 0x48 && *(pkt_data + 0x37+ offsetNum) == 0x54 && \
            *(pkt_data + 0x38+ offsetNum) == 0x54 && *(pkt_data + 0x39+ offsetNum) == 0x50){
            flag = 1; // HTTP
        }

        if(header->caplen <= 54){
            flag = 0;
        }

        if(flag){
            printf("\n");
            // calculate port number;
            int s_port_f = *(pkt_data + 34+ offsetNum);
            int s_port_s = *(pkt_data + 35+ offsetNum);
            int d_port_f = *(pkt_data + 36+ offsetNum);
            int d_port_s = *(pkt_data + 37+ offsetNum);
            int s_port = s_port_f * 256 + s_port_s;
            int d_port = d_port_f * 256 + d_port_s;

            //print first line
            printf("%d %d.%d.%d.%d:%d ", no++, *(pkt_data + 26+ offsetNum), *(pkt_data + 27+ offsetNum),\
             *(pkt_data + 28+ offsetNum), *(pkt_data + 29+ offsetNum), s_port);
            printf("%d.%d.%d.%d:%d HTTP ", *(pkt_data + 30+ offsetNum), *(pkt_data + 31+ offsetNum), \
                *(pkt_data + 32+ offsetNum), *(pkt_data + 33+ offsetNum), d_port);
            if(s_port == 80){
                printf("Response\n");
            }
            else if(d_port == 80){
                printf("Request\n");
            }
            
            for(int i= 0x36 + offsetNum;i < header->len;i++){
                printf("%c", *(pkt_data + i));
                if(*(pkt_data + i) == 0x0a){
                    if(*(pkt_data + i-1) == 0x0d && *(pkt_data + i + 1) == 0x0d && *(pkt_data + i + 2) == 0x0a){break;}
                }
            }
        }
    }
    else if(sniff == 2){ // if pack of DNS
        printf("\n");
        // only header
        // calculate port number
        int s_port_f = *(pkt_data + 34+ offsetNum);
        int s_port_s = *(pkt_data + 35+ offsetNum);
        int d_port_f = *(pkt_data + 36+ offsetNum);
        int d_port_s = *(pkt_data + 37+ offsetNum);
        int s_port = s_port_f * 256 + s_port_s;
        int d_port = d_port_f * 256 + d_port_s;

        // print first line
        printf("%d %d.%d.%d.%d:%d ", no++, *(pkt_data + 26+ offsetNum), *(pkt_data + 27+ offsetNum), \
            *(pkt_data + 28+ offsetNum), *(pkt_data + 29+ offsetNum), s_port);
        printf("%d.%d.%d.%d:%d DNS ID : %x%x\n", *(pkt_data + 30+ offsetNum), *(pkt_data + 31+ offsetNum), \
            *(pkt_data + 32+ offsetNum), *(pkt_data + 33+ offsetNum), d_port, *(pkt_data + 42+ offsetNum), *(pkt_data + 43));
        
        // calculate flag number from decimal to binary
        int flag_f = *(pkt_data + 44+ offsetNum);
        int flag_s = *(pkt_data + 45+ offsetNum);
        int flag = flag_f * 256 + flag_s;
        int binaryFormat[16];
        for(int i=0;i<16;i++){
            binaryFormat[16-i-1] = flag % 2;
            flag = flag / 2;
        }

        // print flags
        printf("%d | ", binaryFormat[0]);
        printf("%d%d%d%d | ", binaryFormat[1], binaryFormat[2], binaryFormat[3], binaryFormat[4]);
        printf("%d | %d | %d | %d | ", binaryFormat[5], binaryFormat[6], binaryFormat[7], binaryFormat[8]);
        printf("%d%d%d | ", binaryFormat[9], binaryFormat[10], binaryFormat[11]);
        printf("%d%d%d%d\n", binaryFormat[12], binaryFormat[13], binaryFormat[14], binaryFormat[15]);

        // print others
        printf("QDCOUNT : ");
        if(*(pkt_data + 46 + offsetNum)){
            printf("%x%x\n", *(pkt_data + 46+ offsetNum), *(pkt_data + 47+ offsetNum));
        }
        else{printf("%x\n", *(pkt_data + 47+ offsetNum));}

        printf("ANCOUNT : ");
        if(*(pkt_data + 48 + offsetNum)){
            printf("%x%x\n", *(pkt_data + 48+ offsetNum), *(pkt_data + 49+ offsetNum));
        }
        else{printf("%x\n", *(pkt_data + 49));}

        printf("NSCOUNT : ");
        if(*(pkt_data + 50 + offsetNum)){
            printf("%x%x\n", *(pkt_data + 50+ offsetNum), *(pkt_data + 51+ offsetNum));
        }
        else{printf("%x\n", *(pkt_data + 51+ offsetNum));}

        printf("ARCOUNT : ");
        if(*(pkt_data + 52 + offsetNum)){
            printf("%x%x\n", *(pkt_data + 52+ offsetNum), *(pkt_data + 53+ offsetNum));
        }
        else{printf("%x\n", *(pkt_data + 53+ offsetNum));}
    }
}