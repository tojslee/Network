#include <stdio.h>
#include <pcap.h>
char errbuf[PCAP_ERRBUF_SIZE];
pcap_if_t *allDevs;

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
    int network;
    printf("Select Network: ");
    scanf("%d", &network);
    while(network <= 0 || network > counter){
        printf("Select Network: ");
        scanf("%d", &network);
    }

    // choose whether to sniff
    int sniff;
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

    pcap_t *handle;
    handle = pcap_open_live(dev->name, BUFSIZ, 1, 1000, errbuf);
    if(handle == NULL){
        printf("Cannot open device %s : %s\n", dev->name, errbuf);
        pcap_freealldevs(allDevs);
        return 0;
    }

    //pcal_loop(handle, 0, parsing, NULL);
//
    char *FILTER_RULE = "port 53";
    struct bpf_program fcode;
    printf("1\n");
    if(pcap_compile(handle, &fcode, FILTER_RULE, 1, NULL) < 0){
        printf("pcap compile failed\n");
        pcap_freealldevs(allDevs);
        return 0;
    }

    printf("2\n");
    if(pcap_setfilter(handle, &fcode) < 0){
        printf("pcap compile failed\n");
        pcap_freealldevs(allDevs);
        return 0;
    }

    printf("3\n");
    pcap_loop(handle, 0, parsing, NULL);
    printf("4\n");

    // packet sniffing
    switch(sniff){
    case 1:
        break;
    case 2:
        break;
    }


    pcap_freealldevs(allDevs);
    pcap_close(handle);
    return 0;
}

void parsing(u_char *param, const struct pcap_pkthdr *header, const u_char *pkt_data){
    printf("please\n");
}