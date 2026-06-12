#include <windows.h>
#include <iostream>
#include <string>

using PassThruOpenFn = long(__stdcall*)(void*, unsigned long*);
using PassThruCloseFn = long(__stdcall*)(unsigned long);
using PassThruGetLastErrorFn = long(__stdcall*)(char*);

static std::string GetLastWinError() {
    DWORD err = GetLastError();
    if (err == 0) {
        return "none";
    }

    LPSTR buffer = nullptr;
    const DWORD size = FormatMessageA(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr,
        err,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        reinterpret_cast<LPSTR>(&buffer),
        0,
        nullptr);

    std::string msg = (size && buffer) ? std::string(buffer, size) : "unknown";
    if (buffer) {
        LocalFree(buffer);
    }
    return msg;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "usage: j2534_native_probe <path-to-j2534-dll>\n";
        return 2;
    }

    const std::string dllPath = argv[1];
    HMODULE lib = LoadLibraryA(dllPath.c_str());
    if (!lib) {
        std::cerr << "{\"status\":\"error\",\"stage\":\"load\",\"message\":\""
                  << GetLastWinError() << "\"}" << std::endl;
        return 1;
    }

    auto passThruOpen = reinterpret_cast<PassThruOpenFn>(GetProcAddress(lib, "PassThruOpen"));
    auto passThruClose = reinterpret_cast<PassThruCloseFn>(GetProcAddress(lib, "PassThruClose"));
    auto passThruGetLastError = reinterpret_cast<PassThruGetLastErrorFn>(GetProcAddress(lib, "PassThruGetLastError"));

    if (!passThruOpen || !passThruClose || !passThruGetLastError) {
        std::cerr << "{\"status\":\"error\",\"stage\":\"symbols\",\"message\":\"Required J2534 exports missing\"}" << std::endl;
        FreeLibrary(lib);
        return 1;
    }

    unsigned long deviceId = 0;
    long openStatus = passThruOpen(nullptr, &deviceId);

    if (openStatus != 0) {
        char err[256] = {0};
        passThruGetLastError(err);
        std::cerr << "{\"status\":\"error\",\"stage\":\"open\",\"code\":"
                  << openStatus << ",\"message\":\"" << err << "\"}" << std::endl;
        FreeLibrary(lib);
        return 1;
    }

    long closeStatus = passThruClose(deviceId);
    FreeLibrary(lib);

    if (closeStatus != 0) {
        std::cerr << "{\"status\":\"error\",\"stage\":\"close\",\"code\":"
                  << closeStatus << ",\"message\":\"PassThruClose failed\"}" << std::endl;
        return 1;
    }

    std::cout << "{\"status\":\"ok\",\"message\":\"J2534 DLL probe successful\"}" << std::endl;
    return 0;
}
