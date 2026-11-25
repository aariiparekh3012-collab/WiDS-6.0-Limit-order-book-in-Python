// Golden trace generator. MENTOR TOOL: runs the real C++ engine over a CSV and
// prints, for every command, (1) the events as JSON lines (using the engine's own
// JsonSink) and (2) one "state" JSON line per symbol (top of book + 5 depth levels).
// Same CSV rules as tools/lob_cli.cpp. Usage: golden_gen [--stp newest|oldest|both] file.csv
#include "lob/exchange.h"
#include "lob/json_sink.h"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

using namespace lob;

static std::string trim(const std::string& s) {
    auto a = s.find_first_not_of(" \t\r\n");
    auto b = s.find_last_not_of(" \t\r\n");
    return a == std::string::npos ? "" : s.substr(a, b - a + 1);
}
static std::string upper(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), ::toupper);
    return s;
}
static Side parse_side(const std::string& s) {
    auto u = upper(trim(s));
    if (u == "BUY" || u == "B") return Side::Buy;
    if (u == "SELL" || u == "S") return Side::Sell;
    throw std::runtime_error("bad side");
}
static OrderType parse_type(const std::string& s) {
    auto u = upper(trim(s));
    if (u == "LIMIT" || u == "LMT" || u == "L") return OrderType::Limit;
    if (u == "MARKET" || u == "MKT" || u == "M") return OrderType::Market;
    if (u == "IOC") return OrderType::IOC;
    if (u == "FOK") return OrderType::FOK;
    throw std::runtime_error("bad type");
}
static STPMode parse_stp(const std::string& s) {
    auto u = upper(s);
    if (u == "NEWEST" || u == "CANCEL_NEWEST") return STPMode::CancelNewest;
    if (u == "OLDEST" || u == "CANCEL_OLDEST") return STPMode::CancelOldest;
    if (u == "BOTH" || u == "CANCEL_BOTH") return STPMode::CancelBoth;
    throw std::runtime_error("bad stp");
}

static void levels_json(const std::vector<DepthLevel>& v) {
    std::cout << "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) std::cout << ",";
        std::cout << "[" << v[i].price << "," << v[i].qty << "," << v[i].order_count << "]";
    }
    std::cout << "]";
}

static void state_line(const Exchange& ex, const std::string& sym) {
    auto t = ex.top(sym);
    auto d = ex.depth(sym, 5);
    std::cout << R"({"state":")" << sym << R"(","best_bid":)";
    if (t.best_bid) std::cout << *t.best_bid; else std::cout << "null";
    std::cout << R"(,"bid_qty":)" << t.bid_qty << R"(,"best_ask":)";
    if (t.best_ask) std::cout << *t.best_ask; else std::cout << "null";
    std::cout << R"(,"ask_qty":)" << t.ask_qty << R"(,"bids":)";
    levels_json(d.bids);
    std::cout << R"(,"asks":)";
    levels_json(d.asks);
    std::cout << "}\n";
}

int main(int argc, char** argv) {
    STPMode stp = STPMode::None;
    const char* path = nullptr;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--stp") stp = parse_stp(argv[++i]);
        else path = argv[i];
    }
    if (!path) { std::cerr << "usage: golden_gen [--stp m] file.csv\n"; return 1; }
    std::ifstream in(path);
    if (!in) { std::cerr << "can't open " << path << "\n"; return 1; }

    Exchange ex(stp);
    JsonSink sink(std::cout);
    Timestamp ts = 0;
    std::string line;
    while (std::getline(in, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') continue;
        if (upper(line).find("ID,") == 0) continue;
        std::istringstream ss(line);
        std::string tok;
        std::vector<std::string> f;
        while (std::getline(ss, tok, ',')) f.push_back(trim(tok));
        if (f.empty()) continue;

        if (upper(f[0]) == "CANCEL") {
            if (f.size() < 2) continue;
            ex.cancel(std::stoull(f[1]), sink);
        } else if (upper(f[0]) == "MODIFY") {
            if (f.size() < 4) continue;
            ex.modify(std::stoull(f[1]), std::stoll(f[2]), std::stoll(f[3]), sink);
        } else {
            if (f.size() < 6) continue;
            Order o;
            o.id = std::stoull(f[0]);
            o.symbol = f[1];
            o.side = parse_side(f[2]);
            o.type = parse_type(f[3]);
            o.price = std::stoll(f[4]);
            o.qty = std::stoll(f[5]);
            o.ts = ++ts;
            if (f.size() >= 7 && !f[6].empty()) o.trader_id = std::stoull(f[6]);
            if (!ex.has_symbol(o.symbol)) ex.add_symbol(o.symbol);
            ex.submit(o, sink);
        }
        auto syms = ex.symbols();
        std::sort(syms.begin(), syms.end());
        for (auto& s : syms) state_line(ex, s);
    }
    return 0;
}
