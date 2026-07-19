#ifndef USDNC_FILE_FORMAT_H
#define USDNC_FILE_FORMAT_H

#include "pxr/pxr.h"
#include "pxr/usd/sdf/fileFormat.h"
#include "pxr/base/tf/staticTokens.h"

PXR_NAMESPACE_OPEN_SCOPE

TF_DECLARE_PUBLIC_TOKENS(UsdncFileFormatTokens, ,
    ((Id,      "usdnc"))
    ((Version, "1.0"))
    ((Target,  "usd"))
);

TF_DECLARE_WEAK_AND_REF_PTRS(UsdncFileFormat);

class UsdncFileFormat : public SdfFileFormat {
public:
    UsdncFileFormat();
    bool CanRead(const std::string& filePath) const override;
    bool Read(SdfLayer* layer, const std::string& resolvedPath, bool metadataOnly) const override;
    bool WriteToFile(const SdfLayer& layer, const std::string& filePath, const std::string& comment, const FileFormatArguments& args) const override;

protected:
    SDF_FILE_FORMAT_FACTORY_ACCESS;
    virtual ~UsdncFileFormat();
};

PXR_NAMESPACE_CLOSE_SCOPE

#endif

